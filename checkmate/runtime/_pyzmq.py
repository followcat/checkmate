import time
import threading

import pickle

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
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:5000")
        while len(self.ports) == 0:
            msg = "client1 request for ports"
            socket.send(pickle.dumps((self._name, msg)))
            print(msg)
            self.ports.extend(pickle.loads(socket.recv()))
        socket.close()

    def connect(self, ports):
        if len(ports) == 2:
            self.sender = context.socket(zmq.PUSH)
            self.sender.bind("tcp://127.0.0.1:%i"%ports[1])
            self.reciever = context.socket(zmq.PULL)
            self.reciever.connect("tcp://127.0.0.1:%i"%ports[0])
            #poller = zmq.Poller()
            #poller.register(self.reciever, zmq.POLLIN)
            #for i in range(5):
            #    socks = dict(poller.poll(100))
            #    if self.reciever in socks and socks[self.reciever] == zmq.POLLIN:
            #        print("reciving")
            #        self.recieve_exchange()
            #    self.send_exchange('exchange 01')
            #    i += 1



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
            left_over = (len(self.out_buffer) != 0)
            self.request_lock.release()
            # Send exchange using protocol here
            #

    def process_receive(self):
        incoming_list = []
        # Receive exchange using protocol here
        #
        if len(incoming_list) != 0:
            self.received_lock.acquire()
            for _incoming in incoming_list:
                self.in_buffer.append(_incoming)
            self.received_lock.release()
        


class Registry(threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        super(Client, self).__init__(name=name)
        self.comp_port = {}
        self.start()

    def run(self):
        """"""
        while True:
            msg = pickle.loads(socket.recv())
            name = msg[0]
            print("Got", msg[1])
            port_out = random.Random().randint(6000, 6500)
            port_in = random.Random().randint(7000, 7500)
            self.comp_port[name] = port_out
            socket.send(pickle.dumps([port_out, port_in]))
            self.con_thrd = ConThread(port_out, port_in, name, self.comp_port)
            self.con_thrd.start()



class ConThread(threading.Thread):
    """"""
    def __init__(self, po, pi, name, comp_port):
        """"""
        threading.Thread.__init__(self, name=name)
        self.port_out = po
        self.port_in = pi
        self.comp_name = name
        self.comp_sender = comp_port

    def run(self):
        """"""
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://127.0.0.1:%i"%self.port_out)
        self.comp_sender.update({self.comp_name: self.sender})
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:%i"%self.port_in)
        #self.recv_exchange()

    def recv_exchange(self):
        """"""
        while(True):
            msg = pickle.loads(self.receiver.recv())
            name = msg[0]
            print("receiving from client: " + msg[1])
            self.send_exchange(msg)

    def send_exchange(self, msg):
        """"""
        try:
            sender = self.comp_sender[msg[0]]
        except:
            print("no component registried")
            return
        print("sending " + msg[1] + " to its destination " + msg[0])
        sender.send(pickle.dumps(msg))



@zope.interface.implementer(checkmate.runtime.communication.IProtocol)
class Communication(object):
    """"""
    def initialize(self):
        self.registry = checkmate.runtime.Registry()
        """"""

