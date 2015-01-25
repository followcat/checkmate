import socket
import logging
import threading

import zmq

import checkmate.runtime._threading
import checkmate.runtime._zmq_wrapper
import checkmate.runtime.communication


class Device(checkmate.runtime._threading.Thread):
    """
        >>> import zmq
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> a = sample_app.application.TestData()
        >>> c = checkmate.runtime._pyzmq.Communication()
        >>> c.initialize()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c3 = a.components['C3']
        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c)
        >>> connector.initialize()
        >>> connector.device.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.device.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c2, c)
        >>> connector.initialize()
        >>> connector.device.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.device.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c3, c)
        >>> connector.initialize()
        >>> connector.device.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.device.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> c.close()
    """
    def __init__(self, component=None, communication=None, is_reading=False):
        super().__init__(component.name)
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
        self.poller = checkmate.runtime._zmq_wrapper.Poller()

        self.logger = \
            logging.getLogger('checkmate.runtime.communication.Device')

    def initialize(self):
        """"""
        if self.broadcast_map:
            self.socket_sub.connect("tcp://127.0.0.1:%i" % self._publishport)
            for _cname in self.broadcast_map.values():
                self.socket_sub.setsockopt(zmq.SUBSCRIBE, _cname.encode())
        self.socket_dealer_in.setsockopt(zmq.IDENTITY, self._name.encode())
        self.socket_dealer_in.connect("tcp://127.0.0.1:%i" % self._routerport)
        self.socket_dealer_out.connect("tcp://127.0.0.1:%i" % self._routerport)

    def start(self):
        if self.is_reading:
            if self.socket_sub:
                self.poller.register(self.socket_sub)
            self.poller.register(self.socket_dealer_in)
        super().start()

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                self.socket_sub.close()
                self.socket_dealer_in.close()
                self.socket_dealer_out.close()
                break
            try:
                socks = self.poller.poll_with_timeout()
                for _s in socks:
                    if _s.TYPE == zmq.SUB:
                        _s.recv()
                    exchange = _s.recv_pyobj()
                    self.connector.inbound(exchange)
            except zmq.error.ZMQError as e:
                if not self.check_for_stop():
                    raise e

    def send(self, exchange):
        """"""
        if exchange.broadcast:
            destination = exchange.origin.encode()
        else:
            destination = exchange.destination[0].encode()
        self.socket_dealer_out.send(destination, flags=zmq.SNDMORE)
        self.socket_dealer_out.send_pyobj(exchange)

    def stop(self):
        """"""
        self.logger.debug("%s stop request" % self)
        super().stop()


class Connector(checkmate.runtime.communication.Connector):
    """"""
    def __init__(self, component=None, communication=None, queue=None,
                 is_reading=False):
        super().__init__(component, communication, queue, is_reading)
        self.device = Device(component, communication, is_reading)
        setattr(self.device, 'connector', self)

    def initialize(self):
        self.device.initialize()

    def open(self):
        self.device.start()

    def send(self, exchange):
        self.device.send(self.encoder.encode(exchange))

    def close(self):
        self.device.stop()


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
        >>> c2 = r.application.components['C2']
        >>> simulated_transition = c2.state_machine.transitions[0]
        >>> o = c2_stub.simulate(simulated_transition)
        >>> t = c1_stub.context.state_machine.transitions[0]
        >>> t.is_matching_incoming(o)
        True
        >>> c1_stub.validate(t)
        True
        >>> time.sleep(1)
        >>> r.stop_test()
    """
    connector_class = Connector

    def __init__(self, component=None):
        """"""
        super().__init__(component)
        self.router = Router()

    def start(self):
        """"""
        super().start()
        self.router.start()

    def close(self):
        """"""
        super().close()
        self.router.stop()

    def get_routerport(self):
        return self.router._routerport

    def get_publishport(self):
        return self.router._publishport
