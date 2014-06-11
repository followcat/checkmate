import copy
import logging
import threading

import zmq

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime._pyzmq
import checkmate.runtime.client
import checkmate.timeout_manager
import checkmate.runtime.launcher
import checkmate.runtime._threading


POLLING_TIMEOUT_SEC = 1
VALIDATE_TIMEOUT_SEC = POLLING_TIMEOUT_SEC


class ISut(zope.interface.Interface):
    """"""

class IStub(ISut):
    """"""
    def simulate(self, transition):
        """"""

    def validate(self, transition):
        """"""

class Component(object):
    def __init__(self, component):
        self.context = component
        self.internal_client_list = []
        self.external_client_list = []
        self.server_list = []
        self.logger = logging.getLogger('checkmate.runtime.component.Component')

    def setup(self, runtime):
        self.runtime = runtime

    def initialize(self):
        for _client in self.external_client_list + self.server_list + self.internal_client_list:
            _client.initialize()

    def start(self):
        self.context.start()
        for _client in self.external_client_list + self.server_list + self.internal_client_list:
            _client.start()

    def stop(self):
        self.context.stop()
        for _client in self.external_client_list + self.server_list + self.internal_client_list:
            _client.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        self.logger.info("%s process exchange %s"%(self.context.name, exchanges[0].value))
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s send exchange %s to %s"%(self.context.name, _o.value, _o.destination))
        return output

    def simulate(self, transition):
        output = self.context.simulate(transition)
        for _o in output:
            for client in [_c for _c in self.internal_client_list if _c.name == _o.destination]:
                client.send(_o)
            for client in [_c for _c in self.external_client_list if _c.name == _o.destination]:
                client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s simulate transition and output %s to %s"%(self.context.name, _o.value, _o.destination))
        return output

    def validate(self, transition):
        return self.context.validate(transition)


@zope.interface.implementer(ISut)
@zope.component.adapter(checkmate.component.IComponent)
class Sut(Component):
    """"""


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Component):
    """"""


class ThreadedComponent(Component, checkmate.runtime._threading.Thread):
    """"""
    using_internal_client = False
    using_external_client = True
    reading_external_client = True

    def __init__(self, component):
        #Need to call both ancestors
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.validation_lock = threading.Lock()
        self.zmq_context = zmq.Context.instance()
        self.poller = zmq.Poller()

    def setup(self, runtime):
        super().setup(runtime)
        _application = runtime.application
        if self.using_internal_client:
            connector_factory = checkmate.runtime._pyzmq.Connector
            _communication = runtime.communication_list['default']
            connector = connector_factory(self.context, _communication, is_server=True)
            self.internal_client_list = [self._create_client(self.context, connector, reading_client=self.reading_internal_client),]
            for _component in [_c for _c in _application.components.keys() if _c != self.context.name]:
                if not hasattr(_application.components[_component], 'connector_list'):
                    continue
                for _c in _application.components[_component].connector_list:
                    connector = connector_factory(_application.components[_component], _communication, is_server=False)
                    self.internal_client_list.append(self._create_client(_application.components[_component], connector, reading_client=self.reading_internal_client))
        try:
            if self.using_external_client:
                for connector_factory in self.context.connector_list:
                    _communication = runtime.communication_list['']
                    connector = connector_factory(self.context, _communication, is_server=True)
                    self.server_list.append(self._create_client(self.context, connector))
                for _component in [_c for _c in _application.components.keys() if _c != self.context.name]:
                    if not hasattr(_application.components[_component], 'connector_list'):
                        continue
                    _communication = runtime.communication_list['']
                    for connector_factory in _application.components[_component].connector_list:
                        connector = connector_factory(_application.components[_component], _communication, is_server=False)
                        self.external_client_list.append(self._create_client(_application.components[_component], connector, reading_client=self.reading_external_client))
        except AttributeError:
            pass
        except Exception as e:
            raise e

    def _create_client(self, component, connector, reading_client=True):
        _socket = self.zmq_context.socket(zmq.PULL)
        port = _socket.bind_to_random_port("tcp://127.0.0.1")
        _client = checkmate.runtime.client.ThreadedClient(component=component, connector=connector, address="tcp://127.0.0.1:%i"%port,
                                                       sender_socket=reading_client)
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

    def run(self):
        while True:
            if self.check_for_stop():
                break
            s = dict(self.poller.poll(POLLING_TIMEOUT_SEC * 1000))
            for socket in iter(s):
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    with self.validation_lock:
                        self.process([exchange])

    def simulate(self, transition):
        return super().simulate(transition)

    @checkmate.timeout_manager.WaitOnFalse(0.1)
    def validate(self, transition):
        with self.validation_lock:
            return super().validate(transition)


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(ThreadedComponent, Sut):
    """"""
    using_internal_client = True
    reading_internal_client = True
    using_external_client = False

    def setup(self, runtime):
        super().setup(runtime)
        if hasattr(self.context, 'launch_command'):
            for communication_class in self.runtime.application.communication_list:
                communication_class(self.context)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(component=copy.deepcopy(self.context), runtime=self.runtime)

    def initialize(self):
        if hasattr(self.context, 'launch_command'):
            self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command, component=self.context)
        self.launcher.initialize()
        super(ThreadedSut, self).initialize()

    def start(self):
        self.launcher.start()
        super(ThreadedSut, self).start()

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
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            s = dict(self.poller.poll(POLLING_TIMEOUT_SEC * 1000))
            for socket in s:
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    with self.validation_lock:
                        self.process([exchange])


