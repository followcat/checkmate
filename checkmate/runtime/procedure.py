import time
import copy
import logging

import zope.interface

import nose.plugins.skip

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.interfaces
import checkmate.runtime.pathfinder
import checkmate.timeout_manager


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
        >>> proc = checkmate.runtime.procedure.Procedure(checkmate.test_data.App)

    If you exepct to output an exchange using generic_incoming(), strange things can happen:
    You select the transition that outputs an 'RL':
        >>> transition = c2.state_machine.transitions[2]

    You execute it:
        >>> _incoming = c2.process(transition.generic_incoming(c2.states))[0]

    But you get the wrong output (because it takes the first transition matching
    the generic_incoming (here this is transition index 1)
        >>> _incoming.value
        'AC'

    You better use, the direct simulate() function with exepcted output:
        >>> _incoming = c2.simulate(transition.outgoing[0].factory())[0]
        >>> _incoming.value
        'RL'

        >>> _outgoing = a.components[_incoming.destination].process([_incoming])
        >>> len(_outgoing)
        0
        >>> setattr(proc, 'exchanges', checkmate._tree.Tree(_incoming, [checkmate._tree.Tree(_output, []) for _output in _outgoing]))
        >>> proc(sut)
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
    def __init__(self, application_class=None, test=None, is_setup=False):
        self.test = test
        self.application_class = application_class
        self.is_setup = is_setup
        self.components = []
        self.tran_dict = {}
        self.logger = logging.getLogger('checkmate.runtime.procedure')
        
    def __call__(self, system_under_test, result=None, *args):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime.test_plan
            >>> import checkmate.runtime.registry
            >>> r1 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r1.setup_environment(['C1'])
            >>> r1.start_test()
            >>> r1_c1 = checkmate.runtime.registry.get_registry(r1.reg_key).getUtility(checkmate.component.IComponent, 'C1')
            >>> r1_c2 = checkmate.runtime.registry.get_registry(r1.reg_key).getUtility(checkmate.component.IComponent, 'C2')
            >>> r1_c3 = checkmate.runtime.registry.get_registry(r1.reg_key).getUtility(checkmate.component.IComponent, 'C3')
            >>> r2 = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r2.setup_environment(['C3'])
            >>> r2.start_test()
            >>> r2_c1 = checkmate.runtime.registry.get_registry(r2.reg_key).getUtility(checkmate.component.IComponent, 'C1')
            >>> r2_c2 = checkmate.runtime.registry.get_registry(r2.reg_key).getUtility(checkmate.component.IComponent, 'C2')
            >>> r2_c3 = checkmate.runtime.registry.get_registry(r2.reg_key).getUtility(checkmate.component.IComponent, 'C3')
            >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
            >>> procedures = []
            >>> for p in gen:
            ...     procedures.append(p[0])

            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('True', 'False', 'True', 'False')
            >>> proc = procedures[0]
            >>> proc.exchanges.root.action
            'AC'
            >>> proc(['C1'])
            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('False', 'True', 'True', 'False')
            >>> proc(['C3'])
            >>> (r1_c1.context.states[0].value, r1_c3.context.states[0].value, r2_c1.context.states[0].value, r2_c3.context.states[0].value)
            ('False', 'True', 'False', 'True')
            >>> r1.stop_test()
            >>> r2.stop_test()
        """
        self.result = result
        self.system_under_test = system_under_test
        if len(self.components) == 0:
            self.components = self._extract_components(self.exchanges, [])
        if not self.is_setup and not self._components_match_sut(self.system_under_test):
            return _compatible_skip_test(self, "Procedure components do not match SUT")
        if self.system_under_test is not None and self.application_class is not None:
            self.registry = checkmate.runtime.registry.get_registry((''.join(self.system_under_test), self.application_class))
        self.application = self.registry.getUtility(checkmate.application.IApplication)
        if hasattr(self, 'initial'):
            if not self.application.compare_states(self.initial):
                self.transform_to_initial() 
            if not self.application.compare_states(self.initial):
                return _compatible_skip_test(self, "Procedure components states do not match Initial")
        self._run_from_startpoint(self.exchanges)

    def transform_to_initial(self):
        if self.application.compare_states(self.initial):
            return
        path = checkmate.runtime.pathfinder.get_path_from_pathfinder(self.application, self.initial)
        if len(path) == 0:
            return _compatible_skip_test(self, "Can't find a path to inital state")
        for _procedure in path:
            _procedure(system_under_test=self.system_under_test)

    def _extract_components(self, node, component_list):
        if (node.root.origin is not None and
            node.root.origin != '' and
            node.root.origin not in component_list):
            component_list.append(node.root.origin)
        if (node.root.destination is not None and
            node.root.destination != '' and
            node.root.destination not in component_list):
            component_list.append(node.root.destination)
        for _n in node.nodes:
            component_list = self._extract_components(_n, component_list)
        return component_list

    def _components_match_sut(self, system_under_test):
        for _sut in system_under_test:
            if _sut not in self.components:
                return False
        return True

    def _run_from_startpoint(self, current_node):
        if self.result is not None:
            self.result.startTest(self)  
        stub = self.registry.getUtility(checkmate.component.IComponent, current_node.root.origin)
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
                stub = self.registry.getUtility(checkmate.component.IComponent, _next.root.destination)
                if not stub.validate(_next.root):
                    raise Exception("No exchange '%s' received by component '%s'" %(_next.root.action, _next.root.destination))
        for _next in node.nodes:
            self._follow_up(_next)

    def shortDescription(self):
        """
        Return the procedure name.
        This is required by the nose framework.
        """
        return self.name

