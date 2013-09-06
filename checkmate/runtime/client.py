import time
import copy

import logging
import threading

import zope.interface

import checkmate.logger
import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.interfaces

@zope.interface.implementer(checkmate.runtime.interfaces.IConnection)
class Client(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, name=None):
        self.logger = logging.getLogger('checkmate.runtime.client.Client')
        super(Client, self).__init__(name=name)
        self.received_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.in_buffer = []
        self.out_buffer = []
        self.name = name
        self.logger.info("%s initial"%self)
        connector = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.IProtocol)
        self.connections = connector(name)

    def run(self):
        """"""
        self.logger.info("%s startup"%self)
        while True:
            if self.check_for_stop():
                self.connections.close()
                break
            self.process_receive()

    def stop(self):
        """"""
        self.logger.info("%s stop"%self)
        super(Client, self).stop()

    def send(self, exchange):
        """"""
        destination = exchange.destination
        self.request_lock.acquire()
        self.logger.info("%s send exchange %s to %s"%(self, exchange.value, destination))
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
        if exchange is not None:
            self.logger.info("%s receive exchange %s"%(self, exchange.value))

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

