import time
import copy
import logging

import zope.interface

import nose.plugins.skip

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.test_plan
import checkmate.runtime.component
import checkmate.runtime.interfaces


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
    def __init__(self, test=None):
        self.test = test
        self.components = []
        self.tran_dict = {}
        self.logger = logging.getLogger('checkmate.runtime.procedure')
        
    def __call__(self, system_under_test, result=None, *args):
        """"""
        self.result = result
        self.system_under_test = system_under_test
        if len(self.components) == 0:
            self.components = self._extract_components(self.exchanges, [])
        if not self._components_match_sut(self.system_under_test):
            return _compatible_skip_test(self, "Procedure components do not match SUT")
        if hasattr(self, 'initial'):
            if not self.compare_states(self.initial):
                self.transform_to_initial() 
            if not self.compare_states(self.initial):
                return _compatible_skip_test(self, "Procedure components states do not match Initial")
        self._run_from_startpoint(self.exchanges)

    def transform_to_initial(self):
        if self.compare_states(self.initial):
            return
        application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
        if not hasattr(self, 'itp_transitions'):
            application.get_initial_transitions()
            self.itp_transitions = application.initial_transitions
        states = []
        for _component in list(application.components.values()):
            states.extend(_component.states)
        try:
            _transition = self.get_transition_from_itp(self.initial, states)
        except IndexError as e:
            raise e("no exchange found in itp to initialize the current")
        for (_procedure, *others) in checkmate.runtime.test_plan.TestProcedureInitialGenerator(application_class=type(application), transition_list=[_transition]):
            _procedure(system_under_test=self.system_under_test)
        if not self.compare_states(self.initial):
            self.transform_to_initial()


    def get_transition_from_itp(self, target, current): #, transitions=[]):
        matching = False
        for _t in self.itp_transitions:
            if len(_t.initial) == 1 and _t.initial[0].code == 'Q0':
                #skipping the 'Always run' transition to avoid infinite recursive
                continue
            for _i in _t.initial:
                try:
                    _current = [_s for _s in current if _i.interface.providedBy(_s)].pop(0)
                    if _current != _i.factory():
                        matching = False
                        break
                    else:
                        matching = True
                except IndexError:
                    matching == False
                    break
            if matching:
               return _t
            else:
                continue
        

    def compare_states(self, target):
        """"""
        matching = 0
        application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
        for _target in target:
            for _component in list(application.components.values()):
                try:
                    #Assume at most one state of component implements interface
                    _state = [_s for _s in _component.states if _target.interface.providedBy(_s)].pop(0)
                    if _state == _target.factory():
                        matching += 1
                        break
                    else:
                        break
                except IndexError:
                        continue
        return matching == len(target)

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
    
    def still_busy(self):
        application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
        component_list = application.system_under_test + application.stubs
        for name in component_list:
            _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
            if _component.is_busy():
                return True
        return False

    def wait_till_not_busy(self):
        while self.still_busy():
            pass

    def _run_from_startpoint(self, current_node):
        if self.result is not None:
            self.result.startTest(self)  
        stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, current_node.root.origin)
        stub.simulate(current_node.root)
        self._follow_up(current_node)

        if hasattr(self, 'final'):
            count = 0
            while count < 3:
                if not self.compare_states(self.final):
                    if self.still_busy():
                        count = 0
                    else:
                        #wait for application turning to idle
                        time.sleep(0.1)
                        count += 1
                else:
                    break
            if count == 3:
                self.logger.error('Procedure Failed: Final states are not as expected')
                raise ValueError("Final states are not as expected")

        self.wait_till_not_busy()
        self.logger.info('Procedure Done')
        if self.result is not None:
            self.result.addSuccess(self)
        if self.result is not None:
            self.result.stopTest(self)


    def _follow_up(self, node):
        for _next in node.nodes:
            if _next.root.destination not in self.system_under_test:
                stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, _next.root.destination)
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

