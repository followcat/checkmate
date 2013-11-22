import time
import copy

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
        >>> transition = c2.state_machine.transitions[2]
        >>> _i = c2.process(transition.generic_incoming(c2.states))[0]
        >>> _i.value
        'AC'
        >>> _i = c2.simulate(transition.outgoing[0].factory())[0]
        >>> _i.value
        'RL'
        >>> _o = a.components[_i.destination].process([_i])
        >>> len(_o)
        0
        >>> setattr(proc, 'exchanges', checkmate._tree.Tree(_i, [checkmate._tree.Tree(_output, []) for _output in _o]))
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
        self.unmatching_components = {}
        self.tran_dict = {}
        
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
                if hasattr(self, 'itp_transitions'):
                    self.transform_to_initial() 
                    _runtime = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IRuntime) 
                    _runtime.wait_till_not_busy()
            if not self.compare_states(self.initial):
                return _compatible_skip_test(self, "Procedure components states do not match Initial")

        self._run_from_startpoint(self.exchanges)

    def transform_to_initial(self):
        if self.compare_states(self.initial):
            return
        application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
        states = []
        while(len(list(self.unmatching_components.keys()))>0):
            c_name, target = self.unmatching_components.popitem()
            states.extend(application.components[c_name].states)
        try:
            _transition = self.get_transition_from_itp(self.initial, states)
        except IndexError as e:
            raise e("no exchange found in itp to initialize the current")

        for (_procedure, *others) in checkmate.runtime.test_plan.TestProcedureInitialGenerator(application_class=type(application), transition_list=[_transition]):
            _procedure(system_under_test=self.system_under_test)


    def get_transition_from_itp(self, target, current):
        matching = False
        for _t in self.itp_transitions:
            for _i in _t.initial:
                try:
                    _current = [_s for _s in current if _i.interface.providedBy(_s)].pop(0)
                    if _current != _i.factory():
                        matching = False
                        break
                    else:
                        matching = True
                except IndexError:
                    continue
            for _target in target:
                try:
                    _state = [_f for _f in _t.final if _target.interface == _f.interface].pop(0)
                    if _state.factory() != _target.factory():
                        matching = False
                        break
                    else:
                        matching = True
                except IndexError:
                    continue
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

        _runtime = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IRuntime) 
        _runtime.wait_till_not_busy()
        if hasattr(self, 'final'):
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

