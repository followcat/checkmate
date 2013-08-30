import zope.interface

import nose.plugins.skip

import checkmate.component
import checkmate.runtime.registry
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProcedure)
class Procedure(object):
    def __init__(self, test=None):
        self.test = test
        
    def __call__(self, result, system_under_test, *args):
        """"""
        self.result = result
        if not self._components_match_sut(system_under_test):
            raise nose.plugins.skip.SkipTest("Procedure components do not match SUT")
        self.system_under_test = system_under_test

        self._run_from_startpoint(self.exchanges)
                

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

