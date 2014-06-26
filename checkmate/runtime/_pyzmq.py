import time
import pickle
import logging
import threading

import zmq
import socket

import checkmate.logger
import checkmate.exchange
import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


class Poller(zmq.Poller):
    def poll(self, timeout=None):
        if self.sockets:
            return super().poll(timeout)
        if timeout > 0:
            time.sleep(timeout/1000)
        return []


class Encoder(object):
    def encode(self, exchange):
        dump = (exchange.action, exchange.get_partition_attr())
        return pickle.dumps(dump)

    def decode(self, message, exchange_module):
        load = pickle.loads(message)
        exchange = getattr(exchange_module, load[0])()
        if exchange.partition_attribute:
            setattr(exchange, dir(exchange)[0], load[1])
        return exchange


class Connector(checkmate.runtime.communication.Connector):
    """"""
    def __init__(self, component, exchange_module, communication=None, is_server=False):
        super(Connector, self).__init__(component, communication=communication, is_server=is_server)
        self._name = component.name
        self.exchange_module = exchange_module
        self.port = -1
        self.socket = None
        self.encoder = Encoder()
        self.poller = Poller()
        self.zmq_context = zmq.Context.instance()
        self._initport = -1
        self._initport = self.communication.get_initport()

    def initialize(self):
        super(Connector, self).initialize()
        if self.is_server:
            self.request_ports()

    def request_ports(self):
        self.socket = self.zmq_context.socket(zmq.PULL)
        self.port = self.socket.bind_to_random_port("tcp://127.0.0.1")
        self.poller.register(self.socket, zmq.POLLIN)

        _socket = self.zmq_context.socket(zmq.REQ)
        _socket.connect("tcp://127.0.0.1:%i"%self._initport)
        _socket.send(pickle.dumps((self._name, self.port)))
        return_code = pickle.loads(_socket.recv())
        _socket.close()

    def connect_ports(self):
        if not self.is_server:
            _socket = self.zmq_context.socket(zmq.REQ)
            _socket.connect("tcp://127.0.0.1:%i"%self._initport)
            _socket.send(pickle.dumps((self._name,)))
            self.port = pickle.loads(_socket.recv())
            _socket.close()

            self.socket = self.zmq_context.socket(zmq.PUSH)
            self.socket.connect("tcp://127.0.0.1:%i"%self.port)

    def open(self):
        """"""
        self.connect_ports()

    def close(self):
        self.socket.close()

    def send(self, destination, exchange):
        """"""
        if not self.is_server:
            #no lock require to protect encoder (only pickle)
            self.socket.send(self.encoder.encode(exchange))
            
    def receive(self):
        socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MS))
        if self.socket in socks:
            msg = self.socket.recv()
            if msg != None:
                _exchange = self.encoder.decode(msg, self.exchange_module)
                return _exchange


class Registry(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Registry, self).__init__(name=name)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Registry')
        self.comp_sender = {}
        self.poller = zmq.Poller()
        self.zmq_context = zmq.Context.instance()
        self.socket = self.zmq_context.socket(zmq.REP)
        self.logger.debug("%s init"%self)
        self.get_assign_port_lock = threading.Lock()

        self._initport = self.pickfreeport()
        self.socket.bind("tcp://127.0.0.1:%i"%self._initport)
        self.logger.debug("%s bind port %i to listen port request"%(self, self._initport))
        self.poller.register(self.socket, zmq.POLLIN)


    def run(self):
        """"""
        self.logger.debug("%s startup"%self)
        while True:
            if self.check_for_stop():
                break
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MS))
            for sock in iter(socks):
                if sock == self.socket:
                    self.assign_ports()

    def assign_ports(self):
        """""" 
        _list = pickle.loads(self.socket.recv())
        if len(_list) == 2:
            (name, port) = _list
            self.comp_sender[name] = port
            self.logger.debug("%s bind port %i to send exchange to %s"%(self, port, name))
            self.socket.send(pickle.dumps(0))
        else:
            (name,) = _list
            port = self.comp_sender[name]
            self.socket.send(pickle.dumps(port))

    def stop(self):
        self.logger.debug("%s stop"%self)
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
        >>> r.stop_test()
    """
    connector_class = Connector

    def __init__(self, component=None):
        """"""
        super(Communication, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize"%self)
        self.registry = Registry()

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.registry.start()

    def close(self):
        self.registry.stop()
        self.logger.info("%s close"%self)

    def get_initport(self):
        return self.registry._initport

