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

    def generic_process(self, exchange):
        transition = self.context.get_transition_by_input([exchange])
        try:
            self.process(transition.generic_incoming(self.context.states))
        except:
            raise AttributeError('current state is not a proper state')

    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            for client in self.external_client_list:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        time.sleep(SIMULATE_WAIT_SEC)
        return output


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
    using_internal_client = False
    using_external_client = True
    reading_external_client = True

    def __init__(self, component):
        #Need to call both ancestors
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.zmq_context = zmq.Context.instance()
        self.poller = zmq.Poller()
        self.busy_lock = threading.Lock()
        self.busy_lock.acquire()
        self.isbusy = True
        self.busy_lock.release()
        for (name, factory) in zope.component.getFactoriesFor(checkmate.runtime.interfaces.IProtocol, context=checkmate.runtime.registry.global_registry):
            if name == 'default':
                if self.using_internal_client:
                    self.internal_client = self._create_client(component, factory, self.reading_internal_client)
            else:
                if self.using_external_client:
                    self.external_client_list.append(self._create_client(component, factory, self.reading_external_client))

    def _create_client(self, component, connector_factory, reading_client=True):
        _socket = self.zmq_context.socket(zmq.PULL)
        port = _socket.bind_to_random_port("tcp://127.0.0.1")
        _socket.close()
        _socket = self.zmq_context.socket(zmq.PULL)
        _socket.connect("tcp://127.0.0.1:%i"%port)
        if reading_client:
            self.poller.register(_socket, zmq.POLLIN)
        return checkmate.runtime.client.ThreadedClient(component=self.context, connector=connector_factory, address="tcp://127.0.0.1:%i"%port, sender_socket=reading_client)

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
            if len(s.keys()) == 0:
                self._set_busy(False)
            else:
                self._set_busy(True)
            for socket in iter(s):
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    self.process([exchange])

    def is_busy(self, timeout=0):
        if timeout != 0:
            time.sleep(timeout)
        return self.isbusy

    def _set_busy(self, isbusy=True):
        self.busy_lock.acquire()
        self.isbusy = isbusy
        self.busy_lock.release()


    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            self.internal_client.send(_o)
        checkmate.logger.global_logger.log_exchange(_o)
        time.sleep(SIMULATE_WAIT_SEC)
        return output


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(ThreadedComponent, Sut):
    """"""
    using_internal_client = True
    reading_internal_client = True
    using_external_client = False

    def __init__(self, component):
        #Call ThreadedSut first ancestor: ThreadedComponent expected
        super(ThreadedSut, self).__init__(component)

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
    using_internal_client = True
    reading_internal_client = False
    using_external_client = True
    reading_external_client = True

    def __init__(self, component):
        self.validation_list = []
        self.validation_lock = threading.Lock()
        self.validation_condition = threading.Condition(self.validation_lock)
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component)

    def process(self, exchanges):
        Stub.process(self, exchanges)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            s = dict(self.poller.poll(1000))
            if len(s.keys()) == 0:
                self._set_busy(False)
            else:
                self._set_busy(True)
            for socket in s:
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    self.validation_lock.acquire()
                    self.validation_list.append(exchange)
                    self.validation_lock.release()
                    self.process([exchange])

    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            self.internal_client.send(_o)
            for client in self.external_client_list:
                client.send(_o)
        checkmate.logger.global_logger.log_exchange(_o)
        time.sleep(SIMULATE_WAIT_SEC)
        return output
            
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

