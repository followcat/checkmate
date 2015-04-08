# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys
import logging
import threading
import collections

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
        self.active_run = None
        self.runtime_components = {}
        self.application = application()
        self.application_class = application
        self.communication_list = collections.defaultdict(communication)
        self._registry = checkmate.runtime.registry.RuntimeGlobalRegistry()

        for _k, _c in self.application.communication_list.items():
            self.communication_list[_k] = _c()

        if self.threaded:
            self._registry.registerAdapter(
                checkmate.runtime.component.ThreadedStub,
                (checkmate.interfaces.IComponent,),
                checkmate.runtime.interfaces.IStub)
            self._registry.registerAdapter(
                checkmate.runtime.component.ThreadedSut,
                (checkmate.interfaces.IComponent,),
                checkmate.runtime.interfaces.ISut)
        else:
            self._registry.registerAdapter(
                checkmate.runtime.component.Stub,
                (checkmate.interfaces.IComponent,),
                checkmate.runtime.interfaces.IStub)
            self._registry.registerAdapter(
                checkmate.runtime.component.Sut,
                (checkmate.interfaces.IComponent,),
                checkmate.runtime.interfaces.ISut)

    def setup_environment(self, sut):
        args_to_log = sys.argv[:]
        for index, arg in enumerate(args_to_log):
            if '--components=' in arg or '--sut=' in arg:
                args_to_log[index] = '--sut=' + ','.join(sut)
                break
        else:
            args_to_log.append('--sut=' + ','.join(sut))

        logging.getLogger('checkmate.runtime._runtime.Runtime').info(
            "%s" % args_to_log)
        self.application.sut(sut)

        for component in self.application.stubs:
            stub = self._registry.getAdapter(
                self.application.components[component],
                checkmate.runtime.interfaces.IStub)
            self.runtime_components[component] = stub
            stub.setup(self)

        for component in self.application.system_under_test:
            sut = self._registry.getAdapter(
                self.application.components[component],
                checkmate.runtime.interfaces.ISut)
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
            >>> simulated_transition = a.components['C2'].state_machine.\
                                        transitions[0]
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
        component_list = self.application.stubs +\
                            self.application.system_under_test
        for name in component_list:
            _component = self.runtime_components[name]
            _component.start()
        self.runs_log.info(['State', self.application.visual_dump_states()])
        self.active_run = self.application.starting_run()

    def stop_test(self):
        # Stop stubs last
        for name in self.application.system_under_test +\
                        self.application.stubs:
            _component = self.runtime_components[name]
            _component.stop()
            # if self.threaded:
            #    _component.join()
        for communication in self.communication_list.values():
            communication.close()

        def check_threads():
            return len(threading.enumerate()) == 1
        condition = threading.Condition()
        with condition:
            condition.wait_for(check_threads,
                                checkmate.timeout_manager.THREAD_STOP_SEC)

    @checkmate.report_issue(
        "checkmate/issues/runs_with_initializing_transition.rst", failed=1)
    def execute(self, run, result=None, transform=True, previous_run=None):
        if (transform is True and
                not self.transform_to_initial(run, previous_run)):
            return checkmate.runtime.procedure._compatible_skip_test(
                        "Procedure components states do not match initial")
        for _c in self.runtime_components.values():
            _c.reset()
        if self.call_procedure(run, result):
            self.runs_log.info(['Run', run.root.name])
        else:
            self.runs_log.info(['Exception', self.application.visual_dump_states()])
            return checkmate.runtime.procedure._compatible_skip_test(
                        "Non-threaded SUT do not simulate")
        logging.getLogger('checkmate.runtime._runtime.Runtime').info(
            'Procedure done')

    def transform_to_initial(self, run, previous_run=None):
        if not run.compare_initial(self.application):
            if previous_run is None:
                previous_run = self.active_run
            run_list = checkmate.pathfinder._find_runs(
                            self.application, run, origin=previous_run)
            if len(run_list) == 0:
                checkmate.runtime.procedure._compatible_skip_test(
                    "Can't find a path to initial state")
                return False
            for _run in run_list:
                if not self.call_procedure(_run):
                    return False
        return True

    def call_procedure(self, run, result=None):
        try:
            checkmate.runtime.procedure.Procedure(run)(self, result)
            if run.collected_run is None:
                self.active_run = run
            elif not run.compare_initial(self.application):
                self.active_run = run
        except ValueError:
            return False
        return True
 
