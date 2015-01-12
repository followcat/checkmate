import logging

import nose.plugins.skip

import checkmate.sandbox
import checkmate.pathfinder
import checkmate.application
import checkmate.timeout_manager
import checkmate.runtime.interfaces


def _compatible_skip_test(procedure, message):
    if hasattr(procedure.result, 'addSkip'):
        if procedure.result is not None:
            procedure.result.startTest(procedure)
            procedure.result.addSkip(procedure, message)
            procedure.result.stopTest(procedure)
            return
    raise nose.plugins.skip.SkipTest(message)


class Procedure(object):
    def __init__(self, test=None):
        self.test = test
        self.logger = logging.getLogger('checkmate.runtime.procedure')

    def __call__(self, runtime, result=None, *args):
        """Run procedure in Runtime instance.

        Provided that we use a defined procedure:
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.test_plan
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
            >>> runs = []
            >>> for run in gen:
            ...     runs.append(run[0])

            >>> proc = r.build_procedure(runs[0])
            >>> proc.transitions.root.outgoing[0].code
            'AC'

        And we create two different Runtime instances:
            >>> r1 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r1.setup_environment(['C1'])
            >>> r1.start_test()
            >>> r1_c1 = r1.runtime_components['C1'].context.states[0]
            >>> r1_c3 = r1.runtime_components['C3'].context.states[0]
            >>> (r1_c1.value, r1_c3.value)
            ('True', 'False')

            >>> r2 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
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
            ('False', 'True')
            >>> (r1_c1.value, r1_c3.value) == (r2_c1.value, r2_c3.value)
            False
            >>> r2.execute(runs[0])
            >>> (r1_c1.value, r1_c3.value) == (r2_c1.value, r2_c3.value)
            True

            >>> r1.stop_test(); r2.stop_test()
        """
        self.result = result
        self.runtime = runtime
        if not hasattr(runtime, 'application'):
            #happens with using --with-doctest on checkmate procedure generator
            return _compatible_skip_test(self, "Procedure is given a runtime of type %s with no application" %type(runtime))
        if self.transitions.root.owner in self.runtime.application.system_under_test:
            return _compatible_skip_test(self, "SUT do NOT simulate")
        self.name = self.transitions.root.name
        self._run_from_startpoint()

    def _run_from_startpoint(self):
        if self.result is not None:
            self.result.startTest(self)
        saved_initial = checkmate.sandbox.Sandbox(self.runtime.application)
        stub = self.runtime.runtime_components[self.transitions.root.owner]
        stub.simulate(self.transitions.root)
        self._follow_up(self.transitions)

        if hasattr(self, 'final'):
            @checkmate.timeout_manager.WaitOnFalse(checkmate.timeout_manager.CHECK_COMPARE_STATES_SEC)
            def check_compare_states():
                return self.runtime.application.compare_states(self.final, saved_initial.application.state_list())
            if not check_compare_states():
                self.logger.error('Procedure Failed: Final states are not as expected')
                raise ValueError("Final states are not as expected")
        if self.result is not None:
            self.result.addSuccess(self)
            self.result.stopTest(self)

    def _follow_up(self, node):
        for _next in node.nodes:
            component = self.runtime.runtime_components[_next.root.owner]
            if not component.validate(_next.root):
                raise Exception("No exchange '%s' received by component '%s'" %(_next.root.incoming[0].code, _next.root.owner))
        for _next in node.nodes:
            self._follow_up(_next)

    def shortDescription(self):
        """
        This is required by the nose framework.
        """
        return self.name

