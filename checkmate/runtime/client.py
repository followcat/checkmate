import time
import copy
import socket
import logging

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

    def initialize(self):
        """"""

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
    def __init__(self, component, connector, address, internal=False, sender_socket=False, is_server=False):
        super(ThreadedClient, self).__init__(component)
        self.sender = None
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.name = component.name
        self.internal = internal
        self.component = component
        self.logger.debug("%s initial"%self)
        self.zmq_context = zmq.Context.instance()
        self.connections = connector(self.component, internal=internal, is_server=is_server)
        if sender_socket:
            self.sender = self.zmq_context.socket(zmq.PUSH)
            self.sender.connect(address)

    def initialize(self):
        """"""
        self.connections.initialize()

    def start(self):
        self.connections.open()
        super(ThreadedClient, self).start()

    def run(self):
        """"""
        self.logger.debug("%s startup"%self)
        while True:
            if self.check_for_stop():
                self.connections.close()
                self.logger.debug("%s stop"%self)
                break
            self.process_receive()

    def stop(self):
        """"""
        self.logger.debug("%s stop request"%self)
        super(ThreadedClient, self).stop()

    def send(self, exchange):
        """Use connector to send exchange

        It is up to the connector to manage the thread protection.
        """
        #no lock shared with process_receive() as POLLING timeout is too long
        destination = exchange.destination
        self.connections.send(destination, exchange)
        self.logger.debug("%s send exchange %s to %s"%(self, exchange.value, destination))

    def process_receive(self):
        exchange = self.connections.receive()
        if exchange is not None:
            if self.sender is not None:
                self.sender.send_pyobj(exchange)
                self.logger.debug("%s receive exchange %s"%(self, exchange.value))

