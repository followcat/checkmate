import time
import copy
import socket
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
    def __init__(self, component):
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
    def __init__(self, component, connector, address, sender_socket=False):
        super(ThreadedClient, self).__init__(component)
        self.sender = None
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.request_lock = threading.Lock()
        self.name = component.name
        self.component = component
        self.logger.info("%s initial"%self)
        self.zmq_context = zmq.Context.instance()
        self.connections = connector(self.component)
        if sender_socket:
            self.sender = self.zmq_context.socket(zmq.PUSH)
            self.sender.bind(address)

    def run(self):
        """"""
        self.connections.open()
        self.logger.debug("%s startup"%self)
        while True:
            if self.check_for_stop():
                self.connections.close()
                self.logger.debug("%s stop"%self)
                break
            self.process_receive()

    def stop(self):
        """"""
        self.logger.info("%s stop request"%self)
        super(ThreadedClient, self).stop()

    def send(self, exchange):
        """"""
        destination = exchange.destination
        with self.request_lock:
            self.connections.send(destination, exchange)
            self.logger.info("%s send exchange %s to %s"%(self, exchange.value, destination))

    def process_receive(self):
        with self.request_lock:
            exchange = self.connections.receive()
        if exchange is not None:
            if self.sender is not None:
                self.sender.send_pyobj(exchange)
                self.logger.info("%s receive exchange %s"%(self, exchange.value))

