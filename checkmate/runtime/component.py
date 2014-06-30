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
        self.client = checkmate.runtime.client.ThreadedClient(self.context)
        self.logger = logging.getLogger('checkmate.runtime.component.Component')

    def setup(self, runtime):
        self.runtime = runtime

    def initialize(self):
        self.client.initialize()

    def start(self):
        self.context.start()
        self.client.start()

    def stop(self):
        self.context.stop()
        self.client.stop()

    def process(self, exchanges):
        output = self.context.process(exchanges)
        self.logger.info("%s process exchange %s"%(self.context.name, exchanges[0].value))
        for _o in output:
            for connector in [_c for _c in self.client.connections if _c._name == _o.destination]:
                connector.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s send exchange %s to %s"%(self.context.name, _o.value, _o.destination))
        return output

    def simulate(self, transition):
        output = self.context.simulate(transition)
        for _o in output:
            for connector in [_c for _c in self.client.connections if _c._name == _o.destination]:
                connector.send(_o)
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
    reading_internal_client = False
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

        _socket = self.zmq_context.socket(zmq.PULL)
        port = _socket.bind_to_random_port("tcp://127.0.0.1")
        self.client.set_sender("tcp://127.0.0.1:%i"%port)
        self.poller.register(_socket, zmq.POLLIN)
        self.client.set_exchange_module(_application.exchange_module)

        if self.using_internal_client:
            connector_factory = checkmate.runtime._pyzmq.Connector
            _communication = runtime.communication_list['default']
            if self.reading_internal_client:
                connector = connector_factory(self.context, _application.exchange_module, _communication, is_server=True)
                self.client.add_connector(connector)
            for _component in [_c for _c in _application.components.keys() if _c != self.context.name]:
                if not hasattr(_application.components[_component], 'connector_list'):
                    continue
                if _component in self.runtime.application.system_under_test:
                    for _c in _application.components[_component].connector_list:
                        connector = connector_factory(_application.components[_component], _application.exchange_module, _communication, is_server=False)
                        self.client.add_connector(connector)

        if self.using_external_client:
            for connector_factory in self.context.connector_list:
                _communication = runtime.communication_list['']
                connector = connector_factory(self.context, _application.exchange_module, _communication, is_server=True)
                self.client.add_connector(connector)
            for _component in [_c for _c in _application.components.keys() if _c != self.context.name]:
                if not hasattr(_application.components[_component], 'connector_list'):
                    continue
                _communication = runtime.communication_list['']
                for connector_factory in _application.components[_component].connector_list:
                    connector = connector_factory(_application.components[_component], _application.exchange_module, _communication, is_server=False)
                    self.client.add_connector(connector)

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
            s = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MS))
            for socket in iter(s):
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    with self.validation_lock:
                        self.process([exchange])

    def simulate(self, transition):
        return super().simulate(transition)

    @checkmate.timeout_manager.WaitOnFalse(checkmate.timeout_manager.VALIDATE_WAITONFALSE_TIME, checkmate.timeout_manager.VALIDATE_WAITONFALSE_LOOP)
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
    reading_external_client = False

    def setup(self, runtime):
        super().setup(runtime)
        if hasattr(self.context, 'launch_command'):
            for communication_class in self.runtime.application.communication_list:
                communication_class(self.context)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(component=copy.deepcopy(self.context), runtime=self.runtime)

    def initialize(self):
        if hasattr(self.context, 'launch_command'):
            if hasattr(self.context, 'command_env'):
                self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command, 
                                                                    command_env=self.context.command_env, component=self.context)
            else:
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
            s = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MS))
            for socket in s:
                exchange = socket.recv_pyobj()
                if exchange is not None:
                    with self.validation_lock:
                        self.process([exchange])
