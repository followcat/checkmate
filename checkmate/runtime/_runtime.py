import sys
import logging
import threading

import zope.interface
import zope.component
import zope.component.interfaces

import checkmate.logger
import checkmate.component
import checkmate.pathfinder
import checkmate.application
import checkmate.timeout_manager
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.procedure
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IRuntime)
@zope.component.adapter((checkmate.application.IApplication, checkmate.runtime.interfaces.IProtocol))
class Runtime(object):
    """"""
    def __init__(self, application, communication, threaded=False):
        """"""
        self.threaded = threaded
        self.runtime_components = {}
        self.communication_list = {}
        self.application_class = application
        self.application = application()
        self._registry = checkmate.runtime.registry.RuntimeGlobalRegistry()

        self.communication_list['default'] = communication()

        for _c in self.application.communication_list:
            _communication = _c()
            self.communication_list[''] = _communication

        if self.threaded:
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedStub,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedSut,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.ISut)
        else:
            self._registry.registerAdapter(checkmate.runtime.component.Stub,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.Sut,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.ISut)

    def setup_environment(self, sut):
        args_to_log = sys.argv[:]
        for index, arg in enumerate(args_to_log):
            if '--components=' in arg or '--sut=' in arg:
                args_to_log[index] = '--sut=' + ','.join(sut)
                break
        else:
            args_to_log.append('--sut=' + ','.join(sut))
            
        checkmate.logger.global_logger.start_exchange_logger()
        logging.getLogger('checkmate.runtime._runtime.Runtime').info("%s" % args_to_log)
        self.application.sut(sut)

        for component in self.application.stubs:
            stub = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.IStub)
            self.runtime_components[component] = stub
            stub.setup(self)

        for component in self.application.system_under_test:
            sut = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.ISut)
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
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> ac = sample_app.application.TestData
            >>> cc = checkmate.runtime.communication.Communication
            >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> c2_stub = r.runtime_components['C2']
            >>> checkmate.runtime.component.IStub.providedBy(c2_stub)
            True
            >>> a = r.application
            >>> simulated_transition = a.components['C2'].state_machine.transitions[0]
            >>> o = c2_stub.simulate(simulated_transition) # doctest: +ELLIPSIS
            >>> c1 = r.runtime_components['C1']
            >>> checkmate.runtime.component.IStub.providedBy(c1)
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

        checkmate.logger.global_logger.stop_exchange_logger()

    def build_procedure(self, run, application=None):
        if application is None:
            sandbox = checkmate.sandbox.Sandbox(self.application_class(), run.walk())
            sandbox(run.root, foreign_transitions=True)
            proc = checkmate.runtime.procedure.Procedure(is_setup=False)
        else:
            sandbox = checkmate.sandbox.Sandbox(application)
            sandbox(run.root)
            proc = checkmate.runtime.procedure.Procedure(is_setup=True)
        sandbox.fill_procedure(proc)
        if len(run.nodes) == 0:
            #force checking final from transition if run contains only the root
            proc.final = run.root.final
        return proc

    def execute(self, procedure, result=None, transform=True):
        #if checkmate.runtime.interfaces.IRun.providedBy(procedure):
        #    self.build_procedure(procedure, self.application)
        self._process(procedure, result=result, transform=transform)

    def _process(self, procedure, result=None, transform=True):
        if checkmate.runtime.interfaces.IProcedure.providedBy(procedure):
            if hasattr(procedure, 'initial'):
                if not transform:
                    if not self.application.compare_states(procedure.initial):
                        return checkmate.runtime.procedure._compatible_skip_test(procedure,
                                "Procedure components states do not match Initial")
                else:
                    if not self.transform_to_procedure_initial(procedure):
                        return checkmate.runtime.procedure._compatible_skip_test(procedure,
                                "Procedure components states do not match Initial")
            for _c in self.runtime_components.values():
                _c.reset()
            procedure(self, result)

    def transform_to_procedure_initial(self, procedure):
        if self.application.compare_states(procedure.initial):
            return True
        path = []
        for _run in checkmate.pathfinder._find_runs(self.application, procedure.initial).keys():
            proc = self.build_procedure(_run, self.application)
            path.append(proc)
            self.execute(proc, transform=False)
        if len(path) == 0:
            checkmate.runtime.procedure._compatible_skip_test(procedure, "Can't find a path to inital state")
            return False
        return True


