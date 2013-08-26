import zope.interface

import checkmate.runtime.interfaces

@zope.interface.implementer(checkmate.runtime.interfaces.IProcedure)
class Procedure(object):
    def __init__(self, test=None):
        self.test = test
        
    def __call__(self, result=None, system_under_test=[], *args):
        if result is not None:
            result.startTest(self)  
            result.addSuccess(self)
            result.stopTest(self)
                    

    def shortDescription(self):
        """
        Return the procedure name.
        This is required by the nose framework.
        """
        return self.name

