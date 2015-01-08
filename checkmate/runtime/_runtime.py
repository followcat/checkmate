import sys
import logging
import threading

import checkmate.logger
import checkmate.interfaces
import checkmate.pathfinder
import checkmate.timeout_manager
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.procedure
import checkmate.runtime.interfaces


class Runtime(object):
    """"""
    def __init__(self, application, communication, threaded=False):
        """"""
        self.runs_log = logging.getLogger('runs.runtime')
        self.threaded = threaded
        self.runtime_components = {}
        self.communication_list = {}
        self.application_class = application
        self.application = application()
        self._registry = checkmate.runtime.registry.RuntimeGlobalRegistry()

        self.communication_list['internal'] = communication()

        for _k, _c in self.application.communication_list.items():
            _communication = _c()
            self.communication_list[_k] = _communication

        if self.threaded:
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedStub,
                                                                       (checkmate.interfaces.IComponent,), checkmate.runtime.interfaces.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedSut,
                                                                       (checkmate.interfaces.IComponent,), checkmate.runtime.interfaces.ISut)
        else:
            self._registry.registerAdapter(checkmate.runtime.component.Stub,
                                                                       (checkmate.interfaces.IComponent,), checkmate.runtime.interfaces.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.Sut,
                                                                       (checkmate.interfaces.IComponent,), checkmate.runtime.interfaces.ISut)

    def setup_environment(self, sut):
        args_to_log = sys.argv[:]
        for index, arg in enumerate(args_to_log):
            if '--components=' in arg or '--sut=' in arg:
                args_to_log[index] = '--sut=' + ','.join(sut)
                break
        else:
            args_to_log.append('--sut=' + ','.join(sut))

        logging.getLogger('checkmate.runtime._runtime.Runtime').info("%s" % args_to_log)
        self.application.sut(sut)

        for component in self.application.stubs:
            stub = self._registry.getAdapter(self.application.components[component], checkmate.runtime.interfaces.IStub)
            self.runtime_components[component] = stub
            stub.setup(self)

        for component in self.application.system_under_test:
            sut = self._registry.getAdapter(self.application.components[component], checkmate.runtime.interfaces.ISut)
            self.runtime_components[component] = sut
            sut.setup(self)

        for communication in self.communication_list.values():
            communication.initialize()

        for name in self.application.stubs + self.application.system_under_test:
            _component = self.runtime_components[name]
            _component.initialize()

    def start_test(self):
        """
            >>> import checkmate.component
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.interfaces
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> ac = sample_app.application.TestData
            >>> cc = checkmate.runtime.communication.Communication
            >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> c2_stub = r.runtime_components['C2']
            >>> checkmate.runtime.interfaces.IStub.providedBy(c2_stub)
            True
            >>> a = r.application
            >>> simulated_transition = a.components['C2'].state_machine.transitions[0]
            >>> o = c2_stub.simulate(simulated_transition) # doctest: +ELLIPSIS
            >>> c1 = r.runtime_components['C1']
            >>> checkmate.runtime.interfaces.IStub.providedBy(c1)
            False
            >>> c1.process(o) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> r.stop_test()
        """
        for communication in self.communication_list.values():
            communication.start()
        # Start stubs first
        component_list = self.application.stubs + self.application.system_under_test
        for name in component_list:
            _component = self.runtime_components[name]
            _component.start()
        self.runs_log.info(['State', self.application.visual_dump_states()])

    def stop_test(self):
        # Stop stubs last
        for name in self.application.system_under_test + self.application.stubs:
            _component = self.runtime_components[name]
            _component.stop()
            #if self.threaded:
            #    _component.join()
        for communication in self.communication_list.values():
            communication.close()

        def check_threads():
            return len(threading.enumerate()) == 1
        condition = threading.Condition()
        with condition:
            condition.wait_for(check_threads, checkmate.timeout_manager.THREAD_STOP_SEC)

    def build_procedure(self, run, application=None):
        if application is None:
            application = self.application_class()
            transitions = run.walk()
            foreign_transitions = True
        else:
            transitions = []
            foreign_transitions = False
        sandbox = checkmate.sandbox.Sandbox(application, transitions)
        sandbox(run.root, foreign_transitions=foreign_transitions)
        proc = checkmate.runtime.procedure.Procedure(is_setup=(not foreign_transitions))
        sandbox.fill_procedure(proc)
        if len(run.nodes) == 0:
            #force checking final from transition if run contains only the root
            proc.final = run.root.final
        return proc

    def execute(self, run, result=None, transform=True):
        procedure = self.build_procedure(run)
        if transform is True and not self.transform_to_procedure_initial(procedure):
            return checkmate.runtime.procedure._compatible_skip_test(procedure, "Procedure components states do not match Initial")
        for _c in self.runtime_components.values():
            _c.reset()
        try:
            procedure(self, result)
            self.runs_log.info(['Run', run.root.name])
        except ValueError:
            self.runs_log.info(['Exception', self.application.visual_dump_states()])

    def transform_to_procedure_initial(self, procedure):
        if not self.application.compare_states(procedure.initial):
            run_list = list(checkmate.pathfinder._find_runs(self.application, procedure.initial).keys())
            if len(run_list) == 0:
                checkmate.runtime.procedure._compatible_skip_test(procedure, "Can't find a path to inital state")
                return False
            for run in run_list:
                proc = self.build_procedure(run, self.application)
                proc(self)
        return True
