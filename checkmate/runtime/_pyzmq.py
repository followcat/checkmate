import copy
import time
import pickle
import random
import threading

import zmq

import zope.interface

import checkmate.runtime.communication
import checkmate.runtime._threading

POLLING_TIMOUT_MS = 1000

@zope.interface.implementer(checkmate.runtime.communication.IConnection)
class Client(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        super(Client, self).__init__(name=name)
        self.received_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.in_buffer = []
        self.out_buffer = []
        self.name = name
        self.ports = []
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        self.request_ports()
        self.connect_ports()

    def request_ports(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:5000")
        while len(self.ports) == 0:
            msg = "client1 request for ports"
            socket.send(pickle.dumps((self._name, msg)))
            self.ports.extend(pickle.loads(socket.recv()))
        socket.close()

    def connect_ports(self):
        if len(self.ports) == 2:
            self.request_lock.acquire()
            self.sender = self.context.socket(zmq.PUSH)
            self.sender.bind("tcp://127.0.0.1:%i"%self.ports[1])
            self.request_lock.release()
            self.receiver = self.context.socket(zmq.PULL)
            self.receiver.connect("tcp://127.0.0.1:%i"%self.ports[0])
            self.poller.register(self.receiver, zmq.POLLIN)

    def close_ports(self):
        self.request_lock.acquire()
        self.sender.close()
        self.request_lock.release()
        self.receiver.close()

    def run(self):
        """"""
        while True:
            if self.check_for_stop():
                self.close_ports()
                break
            self.process_receive()

    def send(self, exchange):
        """"""
        self.request_lock.acquire()
        destination = exchange.destination
        msg = pickle.dumps(exchange)
        self.sender.send(pickle.dumps((destination, msg)))
        self.request_lock.release()


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
            
    def process_receive(self):
        incoming_list = []
        socks = dict(self.poller.poll(POLLING_TIMOUT_MS))
        if self.receiver in socks:
            self.received_lock.acquire()
            self.in_buffer.append(pickle.loads(self.receiver.recv()))
            self.received_lock.release()


class Registry(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Registry, self).__init__(name=name)
        self.comp_sender = {}
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:5000")
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
        port_out = random.Random().randint(6000, 6500)
        port_in = random.Random().randint(7000, 7500)
        self.socket.send(pickle.dumps([port_out, port_in]))
        sender = self.context.socket(zmq.PUSH)
        receiver = self.context.socket(zmq.PULL)
        sender.bind("tcp://127.0.0.1:%i"%port_out)
        self.comp_sender[name] = sender
        receiver.connect("tcp://127.0.0.1:%i"%port_in)
        return receiver

    def forward_incoming(self, socket):
        msg = pickle.loads(socket.recv())
        try:
            sender = self.comp_sender[msg[0]]
        except:
            print("no client registried " + msg[0])
            return
        sender.send(msg[1])


@zope.interface.implementer(checkmate.runtime.communication.IProtocol)
class Communication(object):
    """"""
    connection_handler = Client

    def initialize(self):
        """"""
        self.registry = Registry()
        self.registry.start()

    def close(self):
        self.registry.stop()

