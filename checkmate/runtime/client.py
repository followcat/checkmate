import time
import copy
import socket
import pickle
import logging
import threading

import zmq

import zope.interface

import checkmate.logger
import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IConnection)
class Client(object):
    """"""
    def __init__(self, component, protocol=checkmate.runtime.interfaces.IProtocol):
        """"""
        self.name = component.name
        self.component = component

    def start(self):
        """"""

    def stop(self):
        """"""

    def send(self, exchange):
        """"""

    def read(self):
        """"""

    def received(self, exchange):
        return False


@zope.interface.implementer(checkmate.runtime.interfaces.IConnection)
class ThreadedClient(checkmate.runtime._threading.Thread):
    """"""
    def __init__(self, component, address, protocol=checkmate.runtime.interfaces.IProtocol):
        super(ThreadedClient, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.request_lock = threading.Lock()
        self.name = component.name
        self.component = component
        self.logger.info("%s initial"%self)
        self.zmq_context = zmq.Context()
        self.sender = self.zmq_context.socket(zmq.PUSH)
        self.sender.bind(address)
        connector = checkmate.runtime.registry.global_registry.getUtility(protocol)
        self.connections = connector(self.component)

    def run(self):
        """"""
        self.logger.info("%s startup"%self)
        self.connections.open()
        while True:
            if self.check_for_stop():
                self.connections.close()
                break
            self.process_receive()

    def stop(self):
        """"""
        self.logger.info("%s stop"%self)
        super(ThreadedClient, self).stop()

    def send(self, exchange):
        """"""
        destination = exchange.destination
        self.request_lock.acquire()
        self.connections.send(destination, exchange)
        self.request_lock.release()
        self.logger.info("%s send exchange %s to %s"%(self, exchange.value, destination))

    def process_receive(self):
        self.request_lock.acquire()
        exchange = self.connections.receive()
        self.request_lock.release()
        if exchange is not None:
            self.sender.send(pickle.dumps(exchange))
            self.logger.info("%s receive exchange %s"%(self, exchange.value))

