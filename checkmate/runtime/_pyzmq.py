import pickle
import logging
import threading

import zmq
import socket

import zope.interface

import checkmate.logger
import checkmate.runtime.client
import checkmate.runtime._threading
import checkmate.runtime.interfaces


POLLING_TIMOUT_MS = 1000


class Encoder(object):
    def encode(self, exchange):
        return pickle.dumps(exchange)

    def decode(self, message):
        return pickle.loads(message)

@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component):
        self.component = component
        self._name = component.name
        self.ports = []
        self.sender = None
        self.receiver = None
        self.encoder = Encoder()
        self.poller = zmq.Poller()
        self.context = zmq.Context()
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

    def send(self, destination, exchange):
        """"""
        msg = self.encoder.encode(exchange)
        self.sender.send(pickle.dumps((destination, msg)))
            
    def receive(self):
        socks = dict(self.poller.poll(POLLING_TIMOUT_MS))
        if self.receiver in socks:
            msg = self.receiver.recv()
            if msg != None:
                return self.encoder.decode(msg)


class Registry(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        """"""
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Registry')
        super(Registry, self).__init__(name=name)
        self.comp_sender = {}
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.logger.info("%s init"%self)
        self.get_assign_port_lock = threading.Lock()
        self.get_assign_port_lock.acquire()
        self._initport = self.pickfreeport()
        self.socket.bind("tcp://127.0.0.1:%i"%self._initport)
        self.get_assign_port_lock.release()
        self.logger.info("%s bind port %i to listen port request"%(self, self._initport))
        self.poller.register(self.socket, zmq.POLLIN)

    def run(self):
        """"""
        self.logger.info("%s startup"%self)
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
        self.logger.info("%s bind port %i to send exchange to %s"%(self, port_out, name))
        self.get_assign_port_lock.acquire()
        port_in = self.pickfreeport()
        receiver.connect("tcp://127.0.0.1:%i"%port_in)
        self.get_assign_port_lock.release()
        self.logger.info("%s listen to port %i to receive exchange from %s"%(self, port_in, name))
        self.socket.send(pickle.dumps([port_out, port_in]))
        return receiver

    def stop(self):
        self.logger.info("%s stop"%self)
        super(Registry, self).stop()

    def forward_incoming(self, socket):
        msg = pickle.loads(socket.recv())
        try:
            sender = self.comp_sender[msg[0]]
            self.logger.info("%s receive exchange, destination %s"%(self, msg[0]))
        except:
            self.logger.error("%s has no client registried %s"%(self, msg[0]))
            return
        sender.send(msg[1])
        self.logger.info("%s forward exchange %s to %s"%(self, msg[1], msg[0]))

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
    connection_handler = checkmate.runtime.client.ThreadedClient
    def initialize(self):
        """"""
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize"%self)
        checkmate.runtime.registry.global_registry.registerUtility(Connector, checkmate.runtime.interfaces.IProtocol) 
        self.registry = Registry()
        Connector._initport = self.registry._initport
        self.registry.start()

    def close(self):
        self.registry.stop()
        self.logger.info("%s close"%self)

