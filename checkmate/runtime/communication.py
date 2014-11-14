import socket
import pickle
import threading

import zmq
import zope.interface

import checkmate.runtime._threading
import checkmate.runtime.interfaces
import checkmate.runtime._zmq_wrapper


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
        self.encoder = encoder
        self.poller = checkmate.runtime._zmq_wrapper.Poller()
        self.zmq_context = zmq.Context.instance()
        self.router = self.zmq_context.socket(zmq.ROUTER)
        self.broadcast_router = self.zmq_context.socket(zmq.ROUTER)
        self.publish = self.zmq_context.socket(zmq.PUB)
        self.get_assign_port_lock = threading.Lock()

        self._routerport = self.pickfreeport()
        self._broadcast_routerport = self.pickfreeport()
        self._publishport = self.pickfreeport()
        self.router.bind("tcp://127.0.0.1:%i" % self._routerport)
        self.broadcast_router.bind("tcp://127.0.0.1:%i" % self._broadcast_routerport)
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
                message = sock.recv_multipart()
                exchange = self.encoder.decode(message[2])
                if sock == self.router:
                    self.router.send(message[1], flags=zmq.SNDMORE)
                    self.router.send_pyobj(exchange)
                if sock == self.broadcast_router:
                    self.publish.send(message[1], flags=zmq.SNDMORE)
                    self.publish.send_pyobj(exchange)

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

    def get_partition_attr(self, partition):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime.communication
            >>> a = sample_app.application.TestData()
            >>> ac = a.components['C1'].state_machine.transitions[0].incoming[0].factory()
            >>> dir(ac)
            ['R']
            >>> encoder = checkmate.runtime.communication.Encoder()
            >>> encoder.get_partition_attr(ac) #doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> dr = a.components['C2'].state_machine.transitions[3].incoming[0].factory()
            >>> dir(dr)
            []
            >>> encoder.get_partition_attr(dr)
            {}
        """
        _partition_dict = {}
        for attr in dir(partition):
            _partition_dict[attr] = getattr(partition, attr)
        return _partition_dict

    def encode(self, exchange):
        dump_data = pickle.dumps((type(exchange), exchange.value, self.get_partition_attr(exchange)))
        return dump_data

    @checkmate.fix_issue("checkmate/issues/decode_attribute.rst")
    def decode(self, message):
        """
        >>> import sample_app.application
        >>> import checkmate.runtime.communication
        >>> ac = sample_app.exchanges.AC()
        >>> encoder = checkmate.runtime.communication.Encoder()
        >>> encode_exchange = encoder.encode(ac)
        >>> decode_exchange = encoder.decode(encode_exchange)
        >>> ac == decode_exchange
        True
        """
        exchange_type, exchange_value, exchange_partition = pickle.loads(message)
        exchange = exchange_type(exchange_value, **exchange_partition)
        return exchange
