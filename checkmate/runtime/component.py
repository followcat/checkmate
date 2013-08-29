import time
import threading

import zope.interface
import zope.component

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime._threading
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
        client = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.communication.IConnection)
        self.connection = client(name=self.context.name)

    def start(self):
        self.context.start()
        self.connection.start()

    def stop(self):
        self.context.stop()
        self.connection.stop()

    def process(self, exchanges, outgoing=None):
        output = self.context.process(exchanges)
        for _o in output:
            self.connection.send(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Sut):
    def simulate(self, exchange):
        transition = self.context.get_transition_by_output([exchange])
        return self.process(transition.generic_incoming(self.context.states), exchange)

    def validate(self, exchange):
        if not self.connection.received(exchange):
            return False
        return True


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(checkmate.runtime._threading.Thread, Sut):
    """"""
    def __init__(self, component):
        Sut.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

    def start(self):
        Sut.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Sut.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            for exchange in self.connection.read():
                self.process([exchange])
            time.sleep(0.05)


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(IStub)
class ThreadedStub(checkmate.runtime._threading.Thread, Stub):
    """"""
    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        Stub.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

    def start(self):
        Stub.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Stub.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            for exchange in self.connection.read():
                self.validation_lock.acquire()
                self.validation_list.append(exchange)
                self.validation_lock.release()
                self.process([exchange])
            time.sleep(0.05)

    def validate(self, exchange):
        result = False
        time.sleep(0.1)
        self.validation_lock.acquire()
        if exchange in self.validation_list:
            self.validation_list.remove(exchange)
            result = True
        self.validation_lock.release()
        return result

    #TODO: Should we protect simulate() and validate() with a Lock





