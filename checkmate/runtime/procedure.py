# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import logging

import nose.plugins.skip

import checkmate.sandbox
import checkmate.pathfinder
import checkmate.application
import checkmate.timeout_manager


def _compatible_skip_test(message):
    raise nose.plugins.skip.SkipTest(message)


class Procedure(object):
    def __init__(self, run, test=None):
        self.result = None
        self.test = test
        self.logger = logging.getLogger('checkmate.runtime.procedure')
        self.blocks = run
        self.initial = run.initial
        self.final = run.final

    def __call__(self, runtime, result=None, *args):
        """Run procedure in Runtime instance.

        Provided that we use a defined procedure:
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.test_plan
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(
            ... sample_app.application.TestData,
            ... checkmate.runtime._pyzmq.Communication,
            ... threaded=True)
            >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(
            ...         sample_app.application.TestData)
            >>> runs = []
            >>> for run in gen:
            ...     runs.append(run[0])

            >>> runs[0].root.outgoing[0].code
            'AC'

        And we create two different Runtime instances:
            >>> r1 = checkmate.runtime._runtime.Runtime(
            ...         sample_app.application.TestData,
            ...         checkmate.runtime._pyzmq.Communication,
            ...         threaded=True)
            >>> r1.setup_environment(['C1'])
            >>> r1.start_test()
            >>> r1_c1 = r1.runtime_components['C1'].context.states[0]
            >>> r1_c3 = r1.runtime_components['C3'].context.states[0]
            >>> (r1_c1.value, r1_c3.value)
            (True, False)

            >>> r2 = checkmate.runtime._runtime.Runtime(
            ...         sample_app.application.TestData,
            ...         checkmate.runtime._pyzmq.Communication,
            ...         threaded=True)
            >>> r2.setup_environment(['C3'])
            >>> r2.start_test()
            >>> r2_c1 = r2.runtime_components['C1'].context.states[0]
            >>> r2_c3 = r2.runtime_components['C3'].context.states[0]
            >>> (r1_c1.value, r1_c3.value) == (r2_c1.value, r2_c3.value)
            True

        When the procedure is run in the provided Runtime instance,
        other instances' components are unaffected when not called.
            >>> r1.execute(runs[0])
            >>> (r1_c1.value, r1_c3.value)
            (False, True)
            >>> (r1_c1.value, r1_c3.value) == (r2_c1.value, r2_c3.value)
            False
            >>> r2.execute(runs[0], previous_run=runs[0])
            >>> (r1_c1.value, r1_c3.value) == (r2_c1.value, r2_c3.value)
            True

            >>> r1.stop_test(); r2.stop_test()
        """
        self.result = result
        self.runtime = runtime
        self.name = self.blocks.root.name
        self._run_from_startpoint()

    def _run_from_startpoint(self):
        _application = self.runtime.application
        if self.result is not None:
            self.result.startTest(self)
        stub = self.runtime.runtime_components[self.blocks.root.owner]
        stub.simulate(self.blocks.root)
        self._follow_up(self.blocks)

        if hasattr(self.blocks, 'final'):
            @checkmate.timeout_manager.WaitOnFalse(
                checkmate.timeout_manager.CHECK_COMPARE_STATES_SEC)
            def check_compare_states():
                return self.blocks.compare_final(self.runtime.application)
            if not check_compare_states():
                self.logger.error(
                    'Procedure Failed: Final states are not as expected')
                raise ValueError("Final states are not as expected")
        if self.result is not None:
            self.result.addSuccess(self)
            self.result.stopTest(self)

    def _follow_up(self, node):
        for _next in node.nodes:
            component = self.runtime.runtime_components[_next.root.owner]
            if not component.validate(_next.validate_items):
                raise Exception("No exchange '%s' received by component '%s'"
                            % (_next.root.incoming[0].code, _next.root.owner))
        for _next in node.nodes:
            self._follow_up(_next)

    def shortDescription(self):
        """
        This is required by the nose framework.
        """
        return self.name
