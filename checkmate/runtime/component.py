import copy
import time
import socket
import threading

import zmq

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime.client
import checkmate.runtime.registry
import checkmate.runtime.launcher
import checkmate.runtime._threading
import checkmate.runtime.interfaces


SIMULATE_WAIT_SEC = 0.2
VALIDATE_TIMEOUT_SEC = 0.1


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
        self.internal_client = checkmate.runtime.client.Client(component=self.context)
        self.external_client_list = []

    def start(self):
        self.context.start()
        for client in self.external_client_list:
            client.start()
        self.internal_client.start()

    def stop(self):
        self.context.stop()
        for client in self.external_client_list:
            client.stop()
        self.internal_client.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            for client in self.external_client_list:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
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
            self.internal_client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Component):
    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            self.internal_client.send(_o)
            for client in self.external_client_list:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        return output

    def validate(self, exchange):
        if not self.internal_client.received(exchange):
            return False
        return True


class ThreadedComponent(Component, checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component, poll_socket=True):
        #Need to call both ancestors
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.zmq_context = zmq.Context.instance()
        self.poller = zmq.Poller()
        for (name, factory) in zope.component.getFactoriesFor(checkmate.runtime.interfaces.IProtocol, context=checkmate.runtime.registry.global_registry):
            if name != 'default':
                self.external_client_list.append(self._create_client(component, factory, poll_socket))

    def _create_client(self, component, connector_factory, poll_socket):
        read_socket = self.zmq_context.socket(zmq.PULL)
        port = read_socket.bind_to_random_port("tcp://127.0.0.1")
        read_socket.close()
        read_socket = self.zmq_context.socket(zmq.PULL)
        read_socket.connect("tcp://127.0.0.1:%i"%port)
        if poll_socket:
            self.poller.register(read_socket, zmq.POLLIN)
        return checkmate.runtime.client.ThreadedClient(component=self.context, connector=connector_factory,
                                                       address="tcp://127.0.0.1:%i"%port, sender_socket=poll_socket)

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
            s = dict(self.poller.poll(1000))
            for socket in iter(s):
                exchange = socket.recv_pyobj()
                if exchange is not None:
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
        #TODO clean the class tree
        #Do not use the ThreadedComponent.__init__()
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.zmq_context = zmq.Context.instance()
        self.poller = zmq.Poller()

        for (name, factory) in zope.component.getFactoriesFor(checkmate.runtime.interfaces.IProtocol, context=checkmate.runtime.registry.global_registry):
            if name == 'default':
                self.internal_client = self._create_client(component, factory, True)

        if hasattr(component, 'launch_command'):
            self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(component=copy.deepcopy(self.context))

    def process(self, exchanges):
        Sut.process(self, exchanges)

    def stop(self):
        self.launcher.end()
        super(ThreadedSut, self).stop()


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(IStub)
class ThreadedStub(ThreadedComponent, Stub):
    """"""
    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        self.validation_condition = threading.Condition(self.validation_lock)
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component, poll_socket=True)

        for (name, factory) in zope.component.getFactoriesFor(checkmate.runtime.interfaces.IProtocol, context=checkmate.runtime.registry.global_registry):
            if name == 'default':
                self.internal_client = self._create_client(component, factory, False)

    def process(self, exchanges):
        Stub.process(self, exchanges)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            for socket in dict(self.poller.poll(1000)):
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    self.validation_lock.acquire()
                    self.validation_list.append(exchange)
                    self.validation_lock.release()
                    self.process([exchange])

    def validate(self, exchange):
        self._exchange_to_validate = exchange
        try:
            result = False
            self.validation_lock.acquire()
            self.validation_list.remove(self._exchange_to_validate)
            result = True
            self.validation_lock.release()
            return result
        except ValueError:
            result = self.validation_condition.wait_for(self._validate_exchange, timeout=VALIDATE_TIMEOUT_SEC)
            self.validation_lock.release()
            return result
        except Exception as e:
            self.validation_lock.release()
            raise e

    def _validate_exchange(self):
        try:
            result = False
            self.validation_list.remove(self._exchange_to_validate)
            result = True
        finally:
            return result

    def beforeTest(self, result):
        self.validation_lock.acquire()
        self.validation_list = []
        self.validation_lock.release()

