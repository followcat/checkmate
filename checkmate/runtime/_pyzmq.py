import pickle
import logging
import threading

import zmq
import socket

import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


class Connector(checkmate.runtime.communication.Connector):
    """
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
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub.Type == zmq.DEALER, connector.socket_sub == None
        (True, True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c2, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub == None, connector.socket_sub.TYPE == zmq.SUB
        (True, True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c3, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub == None, connector.socket_sub.TYPE == zmq.SUB
        (True, True, True)
        >>> connector.close()

        >>> c.close()
    """
    def __init__(self, component, communication=None, is_reading=True):
        super(Connector, self).__init__(component, communication=communication, is_reading=is_reading)
        self._name = component.name
        self.is_reading = is_reading
        self.broadcast_map = component.broadcast_map
        self.is_publish = component.is_publish

        self.socket_pub = None
        self.socket_sub = None
        self.socket_dealer_in = None
        self.socket_dealer_out = None

        self.zmq_context = zmq.Context.instance()
        self._routerport = self.communication.get_routerport()
        self._broadcast_routerport = self.communication.get_broadcast_routerport()
        self._publishport = self.communication.get_publishport()

    def initialize(self):
        super(Connector, self).initialize()
        if self.is_publish:
            self.socket_pub = self.open_router_socket(zmq.DEALER, self._broadcast_routerport)
        if self.broadcast_map:
            self.socket_sub = self.open_router_socket(zmq.SUB, self._publishport)
            for _cname in self.broadcast_map.values():
                self.socket_sub.setsockopt(zmq.SUBSCRIBE, _cname.encode())
        self.socket_dealer_in = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_in.setsockopt(zmq.IDENTITY, self._name.encode())
        self.socket_dealer_out = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_in.connect("tcp://127.0.0.1:%i" % self._routerport)
        self.socket_dealer_out.connect("tcp://127.0.0.1:%i" % self._routerport)

    def open_router_socket(self, mode, port):
        new_socket = self.zmq_context.socket(mode)
        new_socket.connect("tcp://127.0.0.1:%i" % port)
        return new_socket

    def open(self):
        """"""

    def close(self):
        if self.socket_pub:
            self.socket_pub.close()
        if self.socket_sub:
            self.socket_sub.close()
        self.socket_dealer_in.close()
        self.socket_dealer_out.close()

    def send(self, exchange):
        """"""
        if exchange.broadcast:
            self.socket_pub.send(pickle.dumps([exchange.origin.encode(), self.communication.encoder.encode(exchange)]))
        else:
            self.socket_dealer_out.send(pickle.dumps([exchange.destination[0].encode(), self.communication.encoder.encode(exchange)]))


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
                package = sock.recv_multipart()
                message = pickle.loads(package[1])
                exchange = self.encoder.decode(message[1])
                if sock == self.router:
                    self.router.send(message[0], flags=zmq.SNDMORE)
                    self.router.send_pyobj(exchange)
                if sock == self.broadcast_router:
                    self.publish.send(message[0], flags=zmq.SNDMORE)
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


class Encoder():
    def __init__(self):
        pass

    def encode(self, exchange):
        dump_data = pickle.dumps((type(exchange), exchange.value, exchange.get_partition_attr()))
        return dump_data

    @checkmate.fix_issue("checkmate/issues/decode_attribute.rst")
    def decode(self, message):
        """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> ac = sample_app.exchanges.AC()
        >>> encoder = checkmate.runtime._pyzmq.Encoder()
        >>> encode_exchange = encoder.encode(ac)
        >>> decode_exchange = encoder.decode(encode_exchange)
        >>> ac == decode_exchange
        True
        """
        exchange_type, exchange_value, exchange_partition = pickle.loads(message)
        exchange = exchange_type(exchange_value, **exchange_partition)
        return exchange


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
        self.encoder = Encoder()
        self.router = Router(self.encoder)

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.router.start()

    def close(self):
        self.router.stop()
        self.logger.info("%s close" % self)

    def get_routerport(self):
        return self.router._routerport

    def get_broadcast_routerport(self):
        return self.router._broadcast_routerport

    def get_publishport(self):
        return self.router._publishport
