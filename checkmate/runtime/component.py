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

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            self.connection.send(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Sut):
    def simulate(self, exchange):
        transition = self.context.get_transition_by_output([exchange])
        return self.process(transition.generic_incoming(self.context.states))

    def validate(self, exchange):
        if not self.connection.received(exchange):
            return False
        return True


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(Sut, checkmate.runtime._threading.Thread):
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
class ThreadedStub(ThreadedSut, checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        super(ThreadedStub, self).__init__(component)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            self.validation_lock.acquire()
            for exchange in self.connection.read():
                self.validation_list.append(exchange)
                self.process([exchange])
            self.validation_lock.release()
            time.sleep(0.05)

    def simulate(self, exchange):
        self.validation_lock.acquire()
        transition = self.context.get_transition_by_output([exchange])
        self.process(transition.generic_incoming(self.context.states))
        self.validation_lock.release()

    def validate(self, exchange):
        time.sleep(0.1)
        try:
            result = True
            self.validation_lock.acquire()
            self.validation_list.remove(exchange)
        except ValueError:
            result = False
        finally:
            self.validation_lock.release()
            return result

    def beforeTest(self, result):
        self.validation_lock.acquire()
        self.validation_list = []
        self.validation_lock.release()

