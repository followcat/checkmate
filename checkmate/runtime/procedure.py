import logging

import zope.interface

import nose.plugins.skip

import checkmate.application
import checkmate.timeout_manager
import checkmate.runtime.interfaces
import checkmate.runtime.pathfinder


def _compatible_skip_test(procedure, message):
    """
        >>> import checkmate._tree
        >>> import checkmate.test_data
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime.procedure
        >>> r = checkmate.runtime._runtime.Runtime(checkmate.test_data.App, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> sut = ['C1']
        >>> r.setup_environment(sut)
        >>> r.start_test()
        >>> a = checkmate.test_data.App()
        >>> c2 = a.components['C2']
        >>> a.start()
        >>> proc = checkmate.runtime.procedure.Procedure()

    If you expect to output an exchange using generic_incoming(), strange things can happen:
    You select the transition that outputs an 'RL':
        >>> transition = c2.state_machine.transitions[2]

    You execute it:
        >>> _incoming = c2.process(transition.generic_incoming(c2.states))[0]

    But you get the wrong output (because it takes the first transition matching
    the generic_incoming (here this is transition index 1)
        >>> _incoming.value
        'AC'

    You better use, the direct simulate() function with expected output:
        >>> _incoming = c2.simulate(transition)[0]
        >>> _incoming.value
        'RL'

        >>> _outgoing = a.components[_incoming.destination].process([_incoming])
        >>> len(_outgoing)
        0
        >>> setattr(proc, 'exchanges', checkmate._tree.Tree(_incoming, [checkmate._tree.Tree(_output, []) for _output in _outgoing]))
        >>> proc(r)
        Traceback (most recent call last):
        ...
        unittest.case.SkipTest: Procedure components do not match SUT
        >>> proc._components_match_sut(sut)
        False
        >>> r.stop_test()
    """
    if hasattr(procedure.result, 'addSkip'):
        if procedure.result is not None:
            procedure.result.startTest(procedure)
            procedure.result.addSkip(procedure, message)
            procedure.result.stopTest(procedure)
            return
    raise nose.plugins.skip.SkipTest(message)


@zope.interface.implementer(checkmate.runtime.interfaces.IProcedure)
class Procedure(object):
    def __init__(self, test=None, is_setup=False):
        self.test = test
        self.is_setup = is_setup
        self.components = []
        self.logger = logging.getLogger('checkmate.runtime.procedure')

    def __call__(self, runtime, result=None, *args):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.test_plan
            >>> r1 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r1.setup_environment(['C1'])
            >>> r1.start_test()
            >>> r1_c1 = r1.runtime_components['C1']
            >>> r1_c2 = r1.runtime_components['C2']
            >>> r1_c3 = r1.runtime_components['C3']
            >>> r2 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r2.setup_environment(['C3'])
            >>> r2.start_test()
            >>> r2_c1 = r2.runtime_components['C1']
            >>> r2_c2 = r2.runtime_components['C2']
            >>> r2_c3 = r2.runtime_components['C3']
            >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
            >>> procedures = []
            >>> for p in gen:
            ...     procedures.append(p[0])

            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('True', 'False', 'True', 'False')
            >>> proc = procedures[0]
            >>> proc.transitions.root.incoming[0].factory().action
            'AC'
            >>> proc(r1)
            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('False', 'True', 'True', 'False')
            >>> proc(r2)
            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('False', 'True', 'False', 'True')
            >>> r1.stop_test()
            >>> r2.stop_test()
        """
        self.result = result
        self.runtime = runtime
        if not hasattr(runtime, 'application'):
            #happens with using --with-doctest on checkmate procedure generator
            return _compatible_skip_test(self, "Procedure is given a runtime of type %s with no application" %type(runtime))
        self.application = runtime.application
        self.system_under_test = runtime.application.system_under_test
        if not self.is_setup and not self._components_match_sut(self.system_under_test):
            return _compatible_skip_test(self, "Procedure components do not match SUT")
        if hasattr(self, 'initial'):
            if not self.application.compare_states(self.initial):
                self.transform_to_initial()
            if not self.application.compare_states(self.initial):
                return _compatible_skip_test(self, "Procedure components states do not match Initial")
        self._run_from_startpoint(self.transitions)

    def transform_to_initial(self):
        if self.application.compare_states(self.initial):
            return
        path = checkmate.runtime.pathfinder.get_path_from_pathfinder(self.application, self.initial)
        if len(path) == 0:
            return _compatible_skip_test(self, "Can't find a path to inital state")
        for _procedure in path:
            _procedure(runtime=self.runtime)

    def _components_match_sut(self, system_under_test):
        for _sut in system_under_test:
            if _sut not in self.components:
                return False
        return True

    def _run_from_startpoint(self, current_node):
        if self.result is not None:
            self.result.startTest(self)

        for component in self.application.components.values():
            if current_node.root.outgoing[0].code in component.outgoings:
                stub_name = component.name
                
        stub = self.runtime.runtime_components[stub_name]
        stub.simulate(current_node.root)
        self._follow_up(current_node)

        if hasattr(self, 'final'):
            @checkmate.timeout_manager.WaitOnFalse()
            def check_compare_states():
                return self.application.compare_states(self.final)
            try:
                check_compare_states()
            except ValueError:
                self.logger.error('Procedure Failed: Final states are not as expected')
                raise ValueError("Final states are not as expected")
        if not self.is_setup:
            self.logger.info('Procedure Done')
        if self.result is not None:
            self.result.addSuccess(self)
        if self.result is not None:
            self.result.stopTest(self)

    def _follow_up(self, node):
        for _next in node.nodes:
            if _next.root.destination not in self.system_under_test:
                stub = self.runtime.runtime_components[_next.root.destination]
                exchange = _next.root.incoming[0].factory()
                if not stub.validate(exchange):
                    raise Exception("No exchange '%s' received by component '%s'" %(exchange.action, _next.root.destination))
        for _next in node.nodes:
            self._follow_up(_next)

    def shortDescription(self):
        """
        Return the procedure name.
        This is required by the nose framework.
        """
        return self.name

