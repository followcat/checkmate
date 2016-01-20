# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate.runs
import checkmate.sandbox


class TestProcedureRun1Threaded(checkmate.runs.Run):
    """"""
    def __init__(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> import sample_app.runtime.test_procedure
            >>> app = sample_app.application.TestData
            >>> com = checkmate.runtime._pyzmq.Communication
            >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> test_procedure = sample_app.runtime.test_procedure
            >>> run = test_procedure.TestProcedureRun1Threaded(app)
            >>> nodes = run.nodes[0].nodes
            >>> nodes[2].root.incoming[0].code
            'ARE'
            >>> nodes[2].nodes[0].root.incoming[0].code
            'AP'
            >>> nodes[2].nodes[0].nodes[1].root.incoming[0].code
            'DA'
            >>> r.execute(run)
            >>> r.stop_test()
        """
        application = application_class()
        application.start()
        c2 = application.components['C2']
        runs = checkmate.runs.get_runs_from_transition(application,
                    c2.engine.blocks[0])
        super().__init__(runs[0].root, runs[0].nodes, 
                            states=c2.states, exchanges=runs[0].exchanges)
        self._collected_run = runs[0].collected_run

    def __call__(self):
        pass

    def __str__(self):
        return (self.__class__.__module__ + '.' + 
                self.__class__.__name__ + '()')


class TestProcedureRun2Threaded(checkmate.runs.Run):
    """"""
    def __init__(self, application_class):
        """
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> import sample_app.runtime.test_procedure
            >>> app = sample_app.application.TestData
            >>> com = checkmate.runtime._pyzmq.Communication
            >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> test_procedure = sample_app.runtime.test_procedure
            >>> run = test_procedure.TestProcedureRun2Threaded(app)
            >>> run.root.incoming[0].code
            'PBRL'
            >>> run.nodes[0].root.incoming[0].code
            'RL'
            >>> run.nodes[0].nodes[0].root.incoming[0].code
            'DR'
            >>> r.execute(run, transform=True)
            >>> r.stop_test()
        """
        application = application_class()
        c2 = application.components['C2']
        run_pbac = checkmate.runs.get_runs_from_transition(application,
                        c2.engine.blocks[0])[0]
        box = checkmate.sandbox.Sandbox(application_class)
        box(run_pbac.exchanges)
        transition_rl_index = [_t for _t in c2.engine.blocks
                               if _t.outgoing and _t.outgoing[0].code == 'RL']
        run_pbrl = checkmate.runs.get_runs_from_transition(box.application,
                        transition_rl_index[0])[0]
        _states = box.application.components['C2'].states
        super().__init__(run_pbrl.root, run_pbrl.nodes,
                            states=_states, exchanges=run_pbrl.exchanges)
        self._collected_run = run_pbrl.collected_run

    def __call__(self):
        pass

    def __str__(self):
        return (self.__class__.__module__ + '.' + 
                self.__class__.__name__ + '()')


def TestProcedureGenerator(application_class):
    """
            >>> import sample_app.application
            >>> import sample_app.runtime.test_procedure
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> app = sample_app.application.TestData
            >>> com = checkmate.runtime._pyzmq.Communication
            >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> test_procedure = sample_app.runtime.test_procedure
            >>> generator = test_procedure.TestProcedureGenerator(app)
            >>> for g in generator:
            ...     r.execute(g[0])
            >>> r.stop_test()
    """
    application = application_class()
    c2 = application.components['C2']
    run_pbac = checkmate.runs.get_runs_from_transition(application,
                    c2.engine.blocks[0])[0]
    yield run_pbac, run_pbac.root.name
