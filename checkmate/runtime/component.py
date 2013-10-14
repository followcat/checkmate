import time
import threading

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.launcher
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

class Component(object):
    def __init__(self, component):
        self.context = component
        client = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IConnection)
        self.internal_client = client(component=self.context)

    def start(self):
        self.context.start()
        self.internal_client.start()

    def stop(self):
        self.context.stop()
        self.internal_client.stop()
        if isinstance(self.internal_client, threading.Thread):
            self.internal_client.join()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            checkmate.logger.global_logger.log_exchange(_o)
            self.internal_client.send(_o)
        return output

    def simulate(self, exchange):
        transition = self.context.get_transition_by_output([exchange])
        try:
            return self.process(transition.generic_incoming(self.context.states))
        except:
            raise AttributeError('current state is not a proper state')


@zope.interface.implementer(ISut)
@zope.component.adapter(checkmate.component.IComponent)
class Sut(Component):
    """"""
    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            checkmate.logger.global_logger.log_exchange(_o)
            #TODO forward output to SUT based on SUT communication
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Component):
    def validate(self, exchange):
        if not self.internal_client.received(exchange):
            return False
        return True


class ThreadedComponent(Component, checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component):
        #Need to call both ancestors
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.external_client_list = []
        #TODO Open external client for communication with SUT

    def start(self):
        Component.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Component.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            for exchange in self.internal_client.read():
                self.process([exchange])

    def simulate(self, exchange):
        transition = self.context.get_transition_by_output([exchange])
        try:
            self.process(transition.generic_incoming(self.context.states))
        except:
            raise AttributeError('current state is not a proper state')
        time.sleep(SIMULATE_WAIT_SEC)


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(ThreadedComponent, Sut):
    """"""
    def __init__(self, component):
        super(ThreadedSut, self).__init__(component)
        #TODO Add start up of the SUT
        if hasattr(component, 'launch_command'):
            self.launcher = checkmate.runtime.launcher.launch(component.launch_command)
        else:
            self.launcher = checkmate.runtime.launcher.launch_component(component)

    def stop(self):
        checkmate.runtime.launcher.end(self.launcher)
        super(ThreadedSut, self).stop()


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(IStub)
class ThreadedStub(ThreadedComponent, Stub):
    """"""
    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            for exchange in self.internal_client.read():
                self.validation_lock.acquire()
                self.validation_list.append(exchange)
                self.validation_lock.release()
                self.process([exchange])

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

