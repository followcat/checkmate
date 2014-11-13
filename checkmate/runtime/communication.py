import socket
import logging
import threading

import zmq
import zope.interface

import checkmate.runtime._threading
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component=None, communication=None, is_server=False, is_reading=False, is_broadcast=False):
        self.component = component
        self.is_server = is_server
        self.is_reading = is_reading
        self.is_broadcast = is_broadcast
        self.communication = communication
        self.socket_dealer_in = None
        self.socket_dealer_out = None
        self.socket_pub = None
        self.socket_sub = None

    def initialize(self):
        """"""

    def open(self):
        """"""

    def close(self):
        """"""

    def send(self, exchange):
        """"""

    def receive(self):
        """"""


@zope.interface.implementer(checkmate.runtime.interfaces.ICommunication)
class Communication(object):
    """"""
    def __init__(self, component=None):
        """"""

    def initialize(self):
        """"""

    def start(self):
        """"""

    def close(self):
        """"""


class Router(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, encoder, name=None):
        """"""
        super(Router, self).__init__(name=name)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Router')
        self.encoder = encoder
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
                message = sock.recv_multipart()
                exchange = self.encoder.decode(message[2])
                if sock == self.router:
                    self.router.send(message[1], flags=zmq.SNDMORE)
                    self.router.send_pyobj(exchange)
                if sock == self.broadcast_router:
                    self.publish.send(message[1], flags=zmq.SNDMORE)
                    self.publish.send_pyobj(exchange)

    def stop(self):
        self.logger.debug("%s stop" % self)
        super(Router, self).stop()

    def pickfreeport(self):
        with self.get_assign_port_lock:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.bind(('127.0.0.1', 0))
            addr, port = _socket.getsockname()
            _socket.close()
        return port
