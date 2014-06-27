import logging

import zmq

import zope.interface

import checkmate.logger
import checkmate.runtime._pyzmq
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
    def __init__(self, component):
        super(ThreadedClient, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.name = component.name
        self.component = component

        self.sender = None
        self.connections = []
        self.zmq_context = zmq.Context.instance()
        self.poller = checkmate.runtime._pyzmq.Poller()
        self.logger.debug("%s initial"%self)

    def add_connector(self, connector):
        self.connections.append(connector)

    def set_sender(self, address):
        self.sender = self.zmq_context.socket(zmq.PUSH)
        self.sender.connect(address)

    def initialize(self):
        """"""
        for _c in self.connections:
            _c.initialize()
            if hasattr(_c, 'socket') and _c.socket:
                self.poller.register(_c.socket, zmq.POLLIN)

    def start(self):
        for _c in self.connections:
            _c.open()
        super(ThreadedClient, self).start()

    def run(self):
        """"""
        self.logger.debug("%s startup"%self)
        while True:
            if self.check_for_stop():
                for _c in self.connections:
                    _c.close()
                self.logger.debug("%s stop"%self)
                break
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MS))
            for _s in socks:
                for _c in self.connections:
                    if _c.socket == _s:
                        exchange = _c.receive()
                        if exchange is not None and _c.is_server:
                            self.sender.send_pyobj(exchange)
                            self.logger.info("%s receive exchange %s"%(self, exchange.value))


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
