import zmq
import time
import copy
import pickle

import threading

import zope.interface

import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.interfaces

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
        connector = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IProtocol)
        self.connections = connector(name)

    def run(self):
        """"""
        while True:
            if self.check_for_stop():
                self.connections.close()
                break
            self.process_receive()

    def send(self, exchange):
        """"""
        destination = exchange.destination
        self.request_lock.acquire()
        self.connections.send(destination, exchange)
        self.request_lock.release()

    def read(self):
        self.received_lock.acquire()
        _local_copy = copy.deepcopy(self.in_buffer)
        self.in_buffer = []
        self.received_lock.release()
        return _local_copy

    def process_receive(self):
        exchange = self.connections.receive()
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

