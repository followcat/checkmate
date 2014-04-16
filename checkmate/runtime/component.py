import copy
import time
import logging
import socket
import threading

import zmq

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime._pyzmq
import checkmate.runtime.client
import checkmate.runtime.registry
import checkmate.runtime.launcher
import checkmate.runtime._threading
import checkmate.runtime.interfaces
import checkmate.timeout_manager


SIMULATE_WAIT_SEC = 0.2
POLLING_TIMEOUT_SEC = 1
VALIDATE_TIMEOUT_SEC = POLLING_TIMEOUT_SEC


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
        self.internal_client_list = []
        self.external_client_list = []
        self.server_list = []
        self.logger = logging.getLogger('checkmate.runtime.component.Component')

    def initialize(self):
        for _client in self.external_client_list:
            _client.initialize()
        for _server in self.server_list:
            _server.initialize()
        for _client in self.internal_client_list:
            _client.initialize()

    def start(self):
        self.context.start()
        for _client in self.external_client_list:
            _client.start()
        for _server in self.server_list:
            _server.start()
        for _client in self.internal_client_list:
            _client.start()

    def stop(self):
        self.context.stop()
        for _client in self.external_client_list:
            _client.stop()
        for _server in self.server_list:
            _server.stop()
        for _client in self.internal_client_list:
            _client.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        for _o in output:
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        return output

    @checkmate.timeout_manager.SleepAfterCall()
    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        return output


@zope.interface.implementer(ISut)
@zope.component.adapter(checkmate.component.IComponent)
class Sut(Component):
    """"""
    def process(self, exchanges):
        output = self.context.process(exchanges)
        self.logger.debug("%s process exchange %s sut=%s"%(self.context.name, exchanges[0].value, self.context.reg_key[0]))
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
        return output


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Component):
    def process(self, exchanges):
        output = self.context.process(exchanges)
        self.logger.info("%s process exchange %s sut=%s"%(self.context.name, exchanges[0].value, self.context.reg_key[0]))
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s send exchange %s to %s sut=%s"%(self.context.name, _o.value, _o.destination, self.context.reg_key[0]))
        return output

    def validate(self, exchange):
        for client in [_c for _c in self.internal_client_list if _c.name == self.context.name]:
            if self.internal_client.received(exchange):
                return True
        return False


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

        _registry = checkmate.runtime.registry.get_registry(self.context.reg_key)
        _application = _registry.getUtility(checkmate.application.IApplication)
        if self.using_internal_client:
            self.internal_client_list = [self._create_client(component, checkmate.runtime._pyzmq.Connector, is_server=True, internal=True, reading_client=self.reading_internal_client),]
            for _component in [_c for _c in _application.components.keys() if _c != component.name]:
                for connector in _application.components[_component].connector_list:
                    self.internal_client_list.append(self._create_client(_application.components[_component], checkmate.runtime._pyzmq.Connector, internal=True, reading_client=self.reading_internal_client))
        try:
            if self.using_external_client:
                for connector in self.context.connector_list:
                    self.server_list.append(self._create_client(component, connector, is_server=True))
            if self.using_external_client:
                for _component in [_c for _c in _application.components.keys() if _c != component.name]:
                    for connector in _application.components[_component].connector_list:
                        self.external_client_list.append(self._create_client(_application.components[_component], connector, reading_client=self.reading_external_client))
        except AttributeError:
            pass
        except Exception as e:
            raise e

    def _create_client(self, component, connector_factory, internal=False, reading_client=True, is_server=False):
        _socket = self.zmq_context.socket(zmq.PULL)
        port = _socket.bind_to_random_port("tcp://127.0.0.1")
        _client = checkmate.runtime.client.ThreadedClient(component=component, connector=connector_factory, address="tcp://127.0.0.1:%i"%port,
                                                       internal=internal, sender_socket=reading_client, is_server=is_server, reg_key=self.context.reg_key)
        if reading_client:
            self.poller.register(_socket, zmq.POLLIN)
        else:
            _socket.close()
        return _client

    def start(self):
        Component.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Component.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def process(self, exchanges):
        Component.process(self, exchanges)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            s = dict(self.poller.poll(POLLING_TIMEOUT_SEC * 1000))
            for socket in iter(s):
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    self.process([exchange])

    @checkmate.timeout_manager.SleepAfterCall()
    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
        checkmate.logger.global_logger.log_exchange(_o)
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
            for connector in self.context.connector_list:
                connector.communication(self.context)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(component=copy.deepcopy(self.context))

    def initialize(self):
        if hasattr(self.context, 'launch_command'):
            self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command, component=self.context)
        self.launcher.initialize()
        super(ThreadedSut, self).initialize()

    def start(self):
        self.launcher.start()
        super(ThreadedSut, self).start()

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
            s = dict(self.poller.poll(POLLING_TIMEOUT_SEC * 1000))
            for socket in s:
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    with self.validation_lock:
                        self.validation_list.append(exchange)
                    self.process([exchange])

    @checkmate.timeout_manager.SleepAfterCall()
    def simulate(self, exchange):
        output = self.context.simulate(exchange)
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s simulate exchange %s to %s sut=%s"%(self.context.name, _o.value, _o.destination, self.context.reg_key[0]))
        return output
            
    @checkmate.timeout_manager.WaitOnFalse()
    def validate(self, exchange):
        result = False
        with self.validation_lock:
            try:
                self.validation_list.remove(exchange)
                result = True
            except:
                result = False
        return result

    def beforeTest(self, result):
        with self.validation_lock:
            self.validation_list = []

