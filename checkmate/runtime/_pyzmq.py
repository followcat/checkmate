import copy
import time
import pickle
import random
import threading

import zmq

import zope.interface

import checkmate.runtime.communication


@zope.interface.implementer(checkmate.runtime.communication.IConnection)
class Client(threading.Thread):
    """"""
    def __init__(self, name=None):
        super(Client, self).__init__(name=name)
        self.received_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.stop_lock = threading.Lock()
        self.end = False
        self.in_buffer = []
        self.out_buffer = []
        self.name = name
        self.ports = []
        self.request_ports()
        if len(self.ports) > 1:
            self.connect(self.ports)

    def request_ports(self):
        self.context = zmq.Context()
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:5000")
        while len(self.ports) == 0:
            msg = "client1 request for ports"
            socket.send(pickle.dumps((self._name, msg)))
            print(msg)
            self.ports.extend(pickle.loads(socket.recv()))
        socket.close()

    def connect(self, ports):
        if len(ports) == 2:
            self.sender = self.context.socket(zmq.PUSH)
            self.sender.bind("tcp://127.0.0.1:%i"%ports[1])
            self.reciever = self.context.socket(zmq.PULL)
            self.reciever.connect("tcp://127.0.0.1:%i"%ports[0])

    def run(self):
        """"""
        while(1):
            self.process_request()
            self.stop_lock.acquire()
            if self.end:
                self.stop_lock.release()
                break
            self.stop_lock.release()
            self.process_receive()
            time.sleep(0.1)

    def stop(self):
        self.stop_lock.acquire(timeout=0.3)
        self.end = True
        self.stop_lock.release()

    def send(self, exchange):
        """"""
        self.request_lock.acquire()
        self.out_buffer.append(exchange)
        self.request_lock.release()


    def received(self, exchange):
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
            
    def process_request(self):
        self.request_lock.acquire()
        left_over = (len(self.out_buffer) != 0)
        self.request_lock.release()
        while(left_over):
            self.request_lock.acquire()
            exchange = self.out_buffer.pop()
            destination = exchange.destination
            print("dest: " + destination)
            msg = pickle.dumps(exchange)
            left_over = (len(self.out_buffer) != 0)
            self.request_lock.release()
            self.sender.send(pickle.dumps((destination, msg)))

    def process_receive(self):
        incoming_list = []
        poller = zmq.Poller()
        poller.register(self.reciever, zmq.POLLIN)
        socks = dict(poller.poll(10))
        if self.reciever in socks and socks[self.reciever] == zmq.POLLIN:
            msg = pickle.loads(self.reciever.recv())
            if len(msg) == 2:
                incoming_list.append(pickle.loads(msg[1]))
        if len(incoming_list) != 0:
            self.received_lock.acquire()
            for _incoming in incoming_list:
                self.in_buffer.append(_incoming)
            self.received_lock.release()
        


class Registry(threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Registry, self).__init__(name=name)
        self.stop_lock = threading.Lock()
        self.end = False
        self.comp_sender = {}
        self.start()

    def run(self):
        """"""
        poller = zmq.Poller()
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:5000")
        poller.register(socket, zmq.POLLIN)
        while True:
            socks = dict(poller.poll(10))
            for sock in iter(socks):
                if sock == socket:
                    msg = pickle.loads(socket.recv())
                    name = msg[0]
                    port_out = random.Random().randint(6000, 6500)
                    port_in = random.Random().randint(7000, 7500)
                    socket.send(pickle.dumps([port_out, port_in]))
                    sender = context.socket(zmq.PUSH)
                    receiver = context.socket(zmq.PULL)
                    sender.bind("tcp://127.0.0.1:%i"%port_out)
                    self.comp_sender[name] = sender
                    receiver.connect("tcp://127.0.0.1:%i"%port_in)
                    poller.register(receiver, zmq.POLLIN)
                else:
                    msg = pickle.loads(sock.recv())
                    try:
                        sender = self.comp_sender[msg[0]]
                    except:
                        print("no client registried " + msg[0])
                        return
                    sender.send(pickle.dumps(msg))

    def stop(self):
        self.stop_lock.acquire(timeout=0.5)
        self.end = True
        self.stop_lock.release()


@zope.interface.implementer(checkmate.runtime.communication.IProtocol)
class Communication(object):
    connection_handler = Client

    """"""
    def initialize(self):
        self.registry = Registry()
        """"""

