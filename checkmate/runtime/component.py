import zope.interface
import zope.component

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.communication


class ISut(zope.interface.Interface):
    """"""

class IStub(ISut):
    """"""
    def simulate(self, exchange):
        """"""

    def validate(self, exchange):
        """"""

@zope.interface.implementer(ISut)
@zope.component.adapter(checkmate.component.IComponent)
class Sut(object):
    def __init__(self, component):
        self.context = component
        client = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.communication.IProtocol)
        self.connection = client(name=self.context.name)

    def start(self):
        self.context.start()
        self.connection.start()

    def stop(self):
        self.connection.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            self.connection.send(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Sut):
    def simulate(self, exchanges):
        return self.process(exchanges)

    def validate(self, exchange):
        if not self.connection.received(exchange):
            return False
        return True
