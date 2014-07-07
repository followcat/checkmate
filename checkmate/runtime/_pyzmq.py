import pickle
import logging
import threading

import zmq
import socket

import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


class Connector(checkmate.runtime.communication.Connector):
    """"""
    def __init__(self, component, communication=None, is_server=False, is_broadcast=False):
        super(Connector, self).__init__(component, communication=communication, is_server=is_server, is_broadcast=is_broadcast)
        self._name = component.name
        self.port = -1
        self.socket = None
        self.zmq_context = zmq.Context.instance()
        self._initport = self.communication.get_initport()

    def initialize(self):
        super(Connector, self).initialize()
        if self.is_server:
            self.request_ports()

    def request_ports(self):
        mode = zmq.PULL
        if self.is_broadcast:
            mode = zmq.PUB
        self.socket = self.zmq_context.socket(mode)
        self.port = self.socket.bind_to_random_port("tcp://127.0.0.1")

        _socket = self.zmq_context.socket(zmq.REQ)
        _socket.connect("tcp://127.0.0.1:%i" % self._initport)
        _socket.send(pickle.dumps((self._name, self.port, self.is_broadcast)))
        return_code = pickle.loads(_socket.recv())
        _socket.close()

    def connect_ports(self):
        if not self.is_server:
            mode = zmq.PUSH
            if self.is_broadcast:
                mode = zmq.SUB
            _socket = self.zmq_context.socket(zmq.REQ)
            _socket.connect("tcp://127.0.0.1:%i" % self._initport)
            _socket.send(pickle.dumps((self._name, self.is_broadcast)))
            self.port = pickle.loads(_socket.recv())
            _socket.close()

            self.socket = self.zmq_context.socket(mode)
            self.socket.connect("tcp://127.0.0.1:%i" % self.port)
            if mode == zmq.SUB:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def open(self):
        """"""
        self.connect_ports()

    def close(self):
        self.socket.close()

    def send(self, exchange):
        """"""
        if not self.is_server:
            #no lock require to protect encoder (only pickle)
            self.socket.send(checkmate.runtime.encoder.encode(exchange))


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
        self.logger.debug("%s init" % self)
        self.get_assign_port_lock = threading.Lock()

        self._initport = self.pickfreeport()
        self.socket.bind("tcp://127.0.0.1:%i" % self._initport)
        self.logger.debug("%s bind port %i to listen port request" % (self, self._initport))
        self.poller.register(self.socket, zmq.POLLIN)

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                break
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC))
            for sock in iter(socks):
                if sock == self.socket:
                    self.assign_ports()

    def assign_ports(self):
        """"""
        _list = pickle.loads(self.socket.recv())
        if len(_list) == 3:
            (name, port, is_broadcast) = _list
            key = name
            if is_broadcast:
                key += '_broadcast'
            self.comp_sender[key] = port
            self.logger.debug("%s bind port %i to send exchange to %s" % (self, port, name))
            self.socket.send(pickle.dumps(0))
        else:
            (name, is_broadcast) = _list
            key = name
            if is_broadcast:
                key += '_broadcast'
            port = self.comp_sender[key]
            self.socket.send(pickle.dumps(port))

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
        self.logger.info("%s initialize" % self)
        self.registry = Registry()

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.registry.start()

    def close(self):
        self.registry.stop()
        self.logger.info("%s close" % self)

    def get_initport(self):
        return self.registry._initport
