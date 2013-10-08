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
        
    def __call__(self, system_under_test, result=None, *args):
        """"""
        self.result = result
        if len(self.components) == 0:
            self.components = self._extract_components(self.exchanges, [])
        if not self._components_match_sut(system_under_test):
            return _compatible_skip_test(self, "Procedure components do not match SUT")

        self.system_under_test = system_under_test

        if hasattr(self, 'initial'):
            current = 0
            matching = 0
            initials = copy.deepcopy(self.initial)
            application = checkmate.runtime.registry.global_registry.getUtility(checkmate.application.IApplication)
            for _c in self.components:
                if _c in application.components:
                    for _s in application.components[_c].states:
                        current += 1
                        for _initial in initials:
                            if _s == _initial.factory():
                                matching += 1
                                initials.remove(_initial)
                                break
            if current != matching:
                return _compatible_skip_test(self, "Procedure components states do not match Initial")

        self._run_from_startpoint(self.exchanges)

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
        _origin = current_node.root.origin
        if _origin not in self.system_under_test:
            if self.result is not None:
                self.result.startTest(self)  

            stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, _origin)
            stub.simulate(current_node.root)
            self._follow_up(current_node)

            if self.result is not None:
                self.result.addSuccess(self)
            if self.result is not None:
                self.result.stopTest(self)
        else:    
            for _node in current_node.nodes:
                self._run_from_startpoint(_node)

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

