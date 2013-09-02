import copy
import time
import pickle
import random
import threading

import zmq
import socket

import zope.interface

import checkmate.runtime._threading
import checkmate.runtime.interfaces


POLLING_TIMOUT_MS = 1000


class Encoder(object):
    def encode(self, exchange):
        return pickle.dumps(exchange)

    def decode(self, message):
        return pickle.loads(message)

class Connector(object):
    """"""
    def __init__(self, name, port):
        self._name = name
        self.ports = []
        self.sender = None
        self.receiver = None
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        self._initport = port
        self.request_ports()
        self.connect_ports()

    def request_ports(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:%i"%self._initport)
        while len(self.ports) == 0:
            msg = "client1 request for ports"
            socket.send(pickle.dumps((self._name, msg)))
            self.ports.extend(pickle.loads(socket.recv()))
        socket.close()

    def connect_ports(self):
        if len(self.ports) == 2:
            self.sender = self.context.socket(zmq.PUSH)
            self.sender.bind("tcp://127.0.0.1:%i"%self.ports[1])
            self.receiver = self.context.socket(zmq.PULL)
            self.receiver.connect("tcp://127.0.0.1:%i"%self.ports[0])
            self.poller.register(self.receiver, zmq.POLLIN)

    def close(self):
        self.sender.close()
        self.receiver.close()

    def send(self, destination, msg):
        """"""
        self.sender.send(pickle.dumps((destination, msg)))
            
    def receive(self):
        socks = dict(self.poller.poll(POLLING_TIMOUT_MS))
        if self.receiver in socks:
            return self.receiver.recv()


@zope.interface.implementer(checkmate.runtime.interfaces.IConnection)
class Client(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        super(Client, self).__init__(name=name)
        self.received_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.in_buffer = []
        self.out_buffer = []
        self.name = name
        self.connections = Connector(name, self._initport)
        self.encoder = Encoder()

    def run(self):
        """"""
        while True:
            if self.check_for_stop():
                self.connections.close()
                break
            self.process_receive()

    def send(self, exchange):
        """"""
        msg = self.encoder.encode(exchange)
        destination = exchange.destination
        self.request_lock.acquire()
        self.connections.send(destination, msg)
        self.request_lock.release()

    def read(self):
        self.received_lock.acquire()
        _local_copy = copy.deepcopy(self.in_buffer)
        self.in_buffer = []
        self.received_lock.release()
        return _local_copy

    def process_receive(self):
        message = self.connections.receive()
        if message is not None:
            exchange = self.encoder.decode(message)
            self.received_lock.acquire()
            self.in_buffer.append(exchange)
            self.received_lock.release()

    # Only used by non-threaded Stub
    def received(self, exchange):
        time.sleep(0.1)
        result = False
        self.received_lock.acquire()
        _local_copy = copy.deepcopy(self.in_buffer)
        self.received_lock.release()
        if exchange in _local_copy:
            result = True
            self.received_lock.acquire()
            self.in_buffer.remove(exchange)
            self.received_lock.release()
        return result
            

class Registry(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Registry, self).__init__(name=name)
        self.comp_sender = {}
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.get_assign_port_lock = threading.Lock()
        self.get_assign_port_lock.acquire()
        self._initport = self.pickfreeport()
        self.socket.bind("tcp://127.0.0.1:%i"%self._initport)
        self.get_assign_port_lock.release()
        self.poller.register(self.socket, zmq.POLLIN)

    def run(self):
        """"""
        while True:
            if self.check_for_stop():
                break
            socks = dict(self.poller.poll(POLLING_TIMOUT_MS))
            for sock in iter(socks):
                if sock == self.socket:
                    receiver = self.assign_ports()
                    self.poller.register(receiver, zmq.POLLIN)
                else:
                    self.forward_incoming(sock)

    def assign_ports(self):
        """""" 
        msg = pickle.loads(self.socket.recv())
        name = msg[0]
        sender = self.context.socket(zmq.PUSH)
        receiver = self.context.socket(zmq.PULL)
        self.get_assign_port_lock.acquire()
        port_out = self.pickfreeport()
        sender.bind("tcp://127.0.0.1:%i"%port_out)
        self.get_assign_port_lock.release()
        self.comp_sender[name] = sender
        self.get_assign_port_lock.acquire()
        port_in = self.pickfreeport()
        receiver.connect("tcp://127.0.0.1:%i"%port_in)
        self.get_assign_port_lock.release()
        self.socket.send(pickle.dumps([port_out, port_in]))
        return receiver

    def forward_incoming(self, socket):
        msg = pickle.loads(socket.recv())
        try:
            sender = self.comp_sender[msg[0]]
        except:
            print("no client registried " + msg[0])
            return
        sender.send(msg[1])

    def pickfreeport(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        addr, port = s.getsockname()
        s.close()
        return port

@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Communication(object):
    """
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.test_data
        >>> import checkmate.runtime
        >>> import checkmate.component
        >>> a = checkmate.test_data.App()
        >>> c = checkmate.runtime._pyzmq.Communication()
        >>> r = checkmate.runtime._runtime.Runtime(a, c)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> import checkmate.runtime.registry
        >>> c2_stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
        >>> c1_stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
        >>> simulated_exchange = a.components['C2'].state_machine.transitions[0].outgoing[0].factory()
        >>> simulated_exchange.origin_destination('C2', 'C1')
        >>> o = c2_stub.simulate(simulated_exchange)
        >>> c1_stub.validate(o[0])
        True
        >>> r.stop_test()

    """
    connection_handler = Client

    def initialize(self):
        """"""
        self.registry = Registry()
        Client._initport = self.registry._initport
        Client.encoding_handler = Encoder
        self.registry.start()

    def close(self):
        self.registry.stop()

