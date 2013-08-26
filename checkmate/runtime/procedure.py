import nose.plugins.skip

import zope.interface

import checkmate.component
import checkmate.runtime.registry
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProcedure)
class Procedure(object):
    def __init__(self, test=None):
        self.test = test
        
    def __call__(self, result, system_under_test, *args):
        """"""
        if not self._components_match_sut(system_under_test):
            raise nose.plugins.skip.SkipTest("Procedure components do not match SUT")

        if result is not None:
            result.startTest(self)  

        self.system_under_test = system_under_test
        for _node in self.exchanges.nodes:
            _origin = _node.root.origin
            if _origin not in self.system_under_test:
                stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, _origin)
                stub.simulate(self.exchanges.root)
                self._follow_up(self.exchanges)
                
        if result is not None:
            result.addSuccess(self)
        if result is not None:
            result.stopTest(self)

    def _components_match_sut(self, system_under_test):
        for _sut in system_under_test:
            if _sut not in self.components:
                return False
        return True

    def _follow_up(self, node):
        for _next in node.nodes:
            if _next.root.destination not in self.system_under_test:
                stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, _next.root.destination)
                if not stub.validate(_next.root):
                    raise Exception('Not received')
        for _next in node.nodes:
            self._follow_up(_next)

    def shortDescription(self):
        """
        Return the procedure name.
        This is required by the nose framework.
        """
        return self.name
