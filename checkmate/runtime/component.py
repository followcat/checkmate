import time
import threading

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.interfaces


SIMULATE_WAIT_SEC = 0.2


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
        client = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IConnection)
        self.client = client(component=self.context)

    def start(self):
        self.context.start()
        self.client.start()

    def stop(self):
        self.context.stop()
        self.client.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            checkmate.logger.global_logger.log_exchange(_o)
            self.client.send(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Sut):
    def simulate(self, exchange):
        transition = self.context.get_transition_by_output([exchange])
        try:
            return self.process(transition.generic_incoming(self.context.states))
        except:
            raise AttributeError('current state is not a proper state')

    def validate(self, exchange):
        if not self.client.received(exchange):
            return False
        return True


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(Sut, checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component):
        #Need to call both ancestors
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
            for exchange in self.client.read():
                self.process([exchange])
            time.sleep(checkmate.runtime._threading.SLEEP_WHEN_RUN_SEC)


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(IStub)
class ThreadedStub(ThreadedSut, checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        #Call ThreadedStub first ancestor: ThreadedSut expected
        super(ThreadedStub, self).__init__(component)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            self.validation_lock.acquire()
            for exchange in self.client.read():
                self.validation_list.append(exchange)
                self.process([exchange])
            self.validation_lock.release()
            time.sleep(checkmate.runtime._threading.SLEEP_WHEN_RUN_SEC)

    def simulate(self, exchange):
        self.validation_lock.acquire()
        transition = self.context.get_transition_by_output([exchange])
        try:
            self.process(transition.generic_incoming(self.context.states))
        except:
            raise AttributeError('current state is not a proper state')
        self.validation_lock.release()
        time.sleep(SIMULATE_WAIT_SEC)

    def validate(self, exchange):
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

