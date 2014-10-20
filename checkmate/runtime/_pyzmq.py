import logging
import threading

import zmq
import socket

import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


class Connector(checkmate.runtime.communication.Connector):
    """
        >>> import zmq
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> a = sample_app.application.TestData()
        >>> c = checkmate.runtime._pyzmq.Communication()
        >>> c.initialize()
        >>> c1 = a.components['C1']
        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c, is_server=True, is_broadcast=True)
        >>> connector.initialize()
        >>> connector.socket_in.TYPE == zmq.DEALER, connector.socket_out.TYPE == zmq.DEALER
        (True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c, is_server=True, is_broadcast=False)
        >>> connector.initialize()
        >>> connector.socket_in.TYPE == zmq.DEALER, connector.socket_out == None
        (True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c, is_server=False, is_broadcast=True)
        >>> connector.open()
        >>> connector.socket_in.TYPE == zmq.SUB, connector.socket_out.TYPE == zmq.DEALER
        (True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c, is_server=False, is_broadcast=False)
        >>> connector.open()
        >>> connector.socket_in == None, connector.socket_out.TYPE == zmq.DEALER
        (True, True)
        >>> connector.close()
        >>> c.close()
    """
    def __init__(self, component, communication=None, is_server=False, is_reading=True, is_broadcast=False):
        super(Connector, self).__init__(component, communication=communication, is_server=is_server, is_reading=is_reading, is_broadcast=is_broadcast)
        self._name = component.name
        self.socket_in = None
        self.socket_out = None
        self.zmq_context = zmq.Context.instance()
        self._routerport = self.communication.get_routerport()
        self._broadcast_routerport = self.communication.get_broadcast_routerport()
        self._publishport = self.communication.get_publishport()

    def initialize(self):
        super(Connector, self).initialize()
        if self.is_server:
            self.request_ports()

    def open_router_socket(self, mode, port):
        new_socket = self.zmq_context.socket(mode)
        new_socket.connect("tcp://127.0.0.1:%i" % port)
        return new_socket

    def request_ports(self):
        self.socket_in = self.zmq_context.socket(zmq.DEALER)
        self.socket_in.setsockopt(zmq.IDENTITY, self._name.encode())
        self.socket_in.connect("tcp://127.0.0.1:%i" % self._routerport)
        if self.is_broadcast:
            self.socket_out = self.open_router_socket(zmq.DEALER, self._broadcast_routerport)

    def connect_ports(self):
        if not self.is_server:
            self.socket_out = self.open_router_socket(zmq.DEALER, self._routerport)
            if self.is_broadcast and self.is_reading:
                self.socket_in = self.open_router_socket(zmq.SUB, self._publishport)
                self.socket_in.setsockopt(zmq.SUBSCRIBE, self._name.encode())

    def open(self):
        """"""
        self.connect_ports()

    def close(self):
        for _socket in [self.socket_in, self.socket_out]:
            if _socket is not None:
                _socket.close()

    def send(self, exchange):
        """"""
        if self.socket_out is not None:
            if exchange.broadcast:
                self.socket_out.send_multipart([exchange.origin.encode(), checkmate.runtime.encoder.encode(exchange)])
            else:
                self.socket_out.send_multipart([exchange.destination[0].encode(), checkmate.runtime.encoder.encode(exchange)])


class Registry(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Registry, self).__init__(name=name)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Registry')
        self.poller = zmq.Poller()
        self.zmq_context = zmq.Context.instance()
        self.router = self.zmq_context.socket(zmq.ROUTER)
        self.broadcast_router = self.zmq_context.socket(zmq.ROUTER)
        self.publish = self.zmq_context.socket(zmq.PUB)
        self.logger.debug("%s init" % self)
        self.get_assign_port_lock = threading.Lock()

        self._routerport = self.pickfreeport()
        self._broadcast_routerport = self.pickfreeport()
        self._publishport = self.pickfreeport()
        self.router.bind("tcp://127.0.0.1:%i" % self._routerport)
        self.broadcast_router.bind("tcp://127.0.0.1:%i" % self._broadcast_routerport)
        self.publish.bind("tcp://127.0.0.1:%i" % self._publishport)

        self.poller.register(self.router, zmq.POLLIN)
        self.poller.register(self.broadcast_router, zmq.POLLIN)

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                break
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC))
            for sock in iter(socks):
                if sock == self.router:
                    message = self.router.recv_multipart()
                    self.router.send_multipart([message[1], message[0], message[2]])
                if sock == self.broadcast_router:
                    message = self.broadcast_router.recv_multipart()
                    self.publish.send_multipart(message[1:])

    def stop(self):
        self.logger.debug("%s stop" % self)
        super(Registry, self).stop()

    def pickfreeport(self):
        with self.get_assign_port_lock:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.bind(('127.0.0.1', 0))
            addr, port = _socket.getsockname()
            _socket.close()
        return port


class Communication(checkmate.runtime.communication.Communication):
    """
        >>> import time
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime
        >>> import checkmate.component
        >>> import sample_app.application
        >>> a = sample_app.application.TestData
        >>> c = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(a, c, True)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> c2_stub = r.runtime_components['C2']
        >>> c1_stub = r.runtime_components['C1']
        >>> simulated_transition = r.application.components['C2'].state_machine.transitions[0]
        >>> o = c2_stub.simulate(simulated_transition)
        >>> c1_stub.context.state_machine.transitions[0].is_matching_incoming(o)
        True
        >>> c1_stub.validate(c1_stub.context.state_machine.transitions[0])
        True
        >>> time.sleep(1)
        >>> r.stop_test()
    """
    connector_class = Connector

    def __init__(self, component=None):
        """"""
        super(Communication, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize" % self)
        self.registry = Registry()

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.registry.start()

    def close(self):
        self.registry.stop()
        self.logger.info("%s close" % self)

    def get_routerport(self):
        return self.registry._routerport

    def get_broadcast_routerport(self):
        return self.registry._broadcast_routerport

    def get_publishport(self):
        return self.registry._publishport
