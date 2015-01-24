import socket
import logging
import threading

import zmq

import checkmate.logger
import checkmate.runtime.client
import checkmate.runtime._threading
import checkmate.runtime._zmq_wrapper


class ThreadedClient(checkmate.runtime.client.Client, 
                     checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component, exchange_queue):
        checkmate.runtime._threading.Thread.__init__(self, component)
        super(ThreadedClient, self).__init__(component, exchange_queue)

        self.poller = checkmate.runtime._zmq_wrapper.Poller()

    def start(self):
        if self.internal_connector and self.internal_connector.is_reading:
            if self.internal_connector.socket_sub:
                self.poller.register(self.internal_connector.socket_sub)
            self.poller.register(self.internal_connector.socket_dealer_in)
        for _connector in [_c for _c in self.external_connectors.values()
                           if _c.is_reading]:
            if _connector.socket_sub:
                self.poller.register(_connector.socket_sub)
            self.poller.register(_connector.socket_dealer_in)
        super(ThreadedClient, self).start()
        checkmate.runtime._threading.Thread.start(self)

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                super().stop()
                break
            socks = self.poller.poll_with_timeout()
            for _s in socks:
                if _s.TYPE == zmq.SUB:
                    _s.recv()
                exchange = _s.recv_pyobj()
                super().receive(exchange)

    def stop(self):
        """"""
        self.logger.debug("%s stop request" % self)
        checkmate.runtime._threading.Thread.stop(self)


class Encoder(object):
    """"""
    def encode(self, exchange):
        return exchange

    def decode(self, message):
        return message


class Connector(object):
    """
        >>> import zmq
        >>> import sample_app.application
        >>> import checkmate.runtime.communication
        >>> a = sample_app.application.TestData()
        >>> c = checkmate.runtime.communication.Communication()
        >>> c.initialize()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c3 = a.components['C3']
        >>> connector = checkmate.runtime.communication.Connector(c1, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime.communication.Connector(c2, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime.communication.Connector(c3, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> c.close()
    """
    def __init__(self, component=None, communication=None, queue=None,
                 is_reading=False):
        self.queue = queue
        self.encoder = Encoder()
        self._name = component.name
        self.component = component
        self.broadcast_map = component.broadcast_map

        self.is_reading = is_reading

        self.zmq_context = zmq.Context.instance()
        self.socket_dealer_in = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_out = self.zmq_context.socket(zmq.DEALER)
        self.socket_sub = self.zmq_context.socket(zmq.SUB)

        self.communication = communication
        self._routerport = communication.get_routerport()
        self._publishport = self.communication.get_publishport()

    def initialize(self):
        """"""
        if self.broadcast_map:
            self.socket_sub.connect("tcp://127.0.0.1:%i" % self._publishport)
            for _cname in self.broadcast_map.values():
                self.socket_sub.setsockopt(zmq.SUBSCRIBE, _cname.encode())
        self.socket_dealer_in.setsockopt(zmq.IDENTITY, self._name.encode())
        self.socket_dealer_in.connect("tcp://127.0.0.1:%i" % self._routerport)
        self.socket_dealer_out.connect("tcp://127.0.0.1:%i" % self._routerport)

    def open(self):
        """"""

    def close(self):
        """"""
        self.socket_sub.close()
        self.socket_dealer_in.close()
        self.socket_dealer_out.close()

    def inbound(self, *message):
        self.queue.put(self.encoder.decode(*message))

    def send(self, exchange):
        """"""
        if exchange.broadcast:
            destination = exchange.origin.encode()
        else:
            destination = exchange.destination[0].encode()
        self.socket_dealer_out.send(destination, flags=zmq.SNDMORE)
        self.socket_dealer_out.send_pyobj(exchange)

    def receive(self):
        """"""


class Communication(object):
    """"""
    connector_class = Connector
    def __init__(self, component=None):
        """"""
        self.router = Router()

    def initialize(self):
        """"""

    def start(self):
        """"""
        self.router.start()

    def close(self):
        """"""
        self.router.stop()

    def get_routerport(self):
        return self.router._routerport

    def get_publishport(self):
        return self.router._publishport

    def connector_factory(self, component, queue, is_reading=True):
        return self.connector_class(component, self, queue,
                    is_reading=is_reading)


class Router(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Router, self).__init__(name=name)
        self.poller = checkmate.runtime._zmq_wrapper.Poller()
        self.zmq_context = zmq.Context.instance()
        self.router = self.zmq_context.socket(zmq.ROUTER)
        self.broadcast_router = self.zmq_context.socket(zmq.ROUTER)
        self.publish = self.zmq_context.socket(zmq.PUB)
        self.get_assign_port_lock = threading.Lock()

        self._routerport = self.pickfreeport()
        self._publishport = self.pickfreeport()
        self.router.bind("tcp://127.0.0.1:%i" % self._routerport)
        self.publish.bind("tcp://127.0.0.1:%i" % self._publishport)

        self.poller.register(self.router)
        self.poller.register(self.broadcast_router)

    def run(self):
        """"""
        while True:
            if self.check_for_stop():
                break
            socks = self.poller.poll_with_timeout()
            for sock in iter(socks):
                origin = sock.recv()
                destination = sock.recv()
                exchange = sock.recv_pyobj()
                if exchange.broadcast:
                    self.publish.send(destination, flags=zmq.SNDMORE)
                    self.publish.send_pyobj(exchange)
                else:
                    self.router.send(destination, flags=zmq.SNDMORE)
                    self.router.send_pyobj(exchange)

    def pickfreeport(self):
        with self.get_assign_port_lock:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.bind(('127.0.0.1', 0))
            addr, port = _socket.getsockname()
            _socket.close()
        return port
