import copy

import zope.interface

import nose.plugins.skip

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.interfaces


def _compatible_skip_test(procedure, message):
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
        self.unmatching_components = {}
        self.tran_dict = {}
        
    def __call__(self, system_under_test, result=None, *args):
        """"""
        self.result = result
        if len(self.components) == 0:
            self.components = self._extract_components(self.exchanges, [])
        if not self._components_match_sut(system_under_test):
            return _compatible_skip_test(self, "Procedure components do not match SUT")

        self.system_under_test = system_under_test

        if hasattr(self, 'initial'):
            if not self.compare_states(self.initial):
                application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
                while(len(list(self.unmatching_components.keys()))>0):
                    c_name, target = self.unmatching_components.popitem()
                    self.tran_dict[c_name] = self.state_initialize(application.components[c_name], target)
                return _compatible_skip_test(self, "Procedure components states do not match Initial")

        self._run_from_startpoint(self.exchanges)

    def state_initialize(self, component, target):
        """"""
        tran_list = []
        state = target
        current = copy.deepcopy(component.states)
        transitions = list(component.state_machine.transitions)
        tran_list.extend(self.get_transition(transitions, state, current))
        return tran_list
        

    def get_transition(self, transitions, state, current):
        tran_list = []
        tran_copies = copy.deepcopy(transitions)
        for _tran in tran_copies:
            if _tran.is_matching_initial(current):
                tran_list.append(_tran)
                tran_copies.remove(_tran)
                states = copy.deepcopy(current)
                _tran.generic_process(states)
                _state = [_s for _s in states if state.interface.providedBy(_s)].pop(0)
                if _state == state.factory():
                    return tran_list
                else:
                    tran_list.extend(self.get_transtion(transitions, state, states))
            else:
                continue
        return tran_list

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
                        self.unmatching_components[_component.name] = _target
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
    
    def _run_from_startpoint(self, current_node):
        if self.result is not None:
            self.result.startTest(self)  

        stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, current_node.root.origin)
        stub.simulate(current_node.root)
        self._follow_up(current_node)

        application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication) 
        component_list = application.system_under_test + application.stubs
        if hasattr(self, 'final'):
            busy = True
            while busy:
                for name in component_list:
                    _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
                    if _component.is_busy():
                        busy = True
                        break
                    else:
                        busy = False
            if not self.compare_states(self.final):
                #need to modify A0() to A0(True) in line78 of sample_app/component_3/state_machine.rst to make final states fix
                raise ValueError("Final states are not as expected")
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

