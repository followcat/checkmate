import time
import logging

import zmq
import zope.interface

import checkmate.logger
import checkmate.runtime.encoder
import checkmate.runtime._threading
import checkmate.runtime.interfaces


class Poller(zmq.Poller):
    def poll(self, timeout=None):
        if self.sockets:
            return super().poll(timeout)
        if timeout > 0:
            time.sleep(timeout / 1000)
        return []


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
    """
        >>> import time
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.component
        >>> ac = sample_app.application.TestData
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded=True)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> rc1 = r.runtime_components['C1']
        >>> rc2 = r.runtime_components['C2']
        >>> rc3 = r.runtime_components['C3']
        >>> are = sample_app.exchanges.ARE()
        >>> are._destination = ['C2']
        >>> rc1.client.send(are)
        >>> time.sleep(0.5)
        >>> rc2.context.validation_list.all_items()[0].action
        'ARE'
        >>> rc2.reset()
        >>> rc3.reset()
        >>> pa = sample_app.exchanges.PA()
        >>> pa._origin = 'C1'
        >>> pa.broadcast
        True
        >>> rc1.client.send(pa)
        >>> time.sleep(0.5)
        >>> import time; time.sleep(1)
        >>> rc2.context.validation_list.all_items()[0].action
        'PA'
        >>> rc3.context.validation_list.all_items()[0].action
        'PA'
        >>> r.stop_test()
    """
    def __init__(self, component):
        super(ThreadedClient, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.name = component.name
        self.component = component

        self.sender = None
        self.connections = []
        self.zmq_context = zmq.Context.instance()
        self.poller = Poller()
        self.logger.debug("%s initial" % self)

    def add_connector(self, connector):
        self.connections.append(connector)

    def set_sender(self, address):
        self.sender = self.zmq_context.socket(zmq.PUSH)
        self.sender.connect(address)

    def set_exchange_module(self, exchange_module):
        self.exchange_module = exchange_module

    def initialize(self):
        """"""
        for _c in self.connections:
            _c.initialize()

    def start(self):
        for _c in self.connections:
            _c.open()
            if not _c.is_reading:
                continue
            if hasattr(_c, 'socket_in') and _c.socket_in is not None:
                self.poller.register(_c.socket_in, zmq.POLLIN)
        super(ThreadedClient, self).start()

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                for _c in self.connections:
                    _c.close()
                self.logger.debug("%s stop" % self)
                break
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC))
            for _s in socks:
                msg = _s.recv_multipart()
                msg = msg[-1]
                exchange = checkmate.runtime.encoder.decode(msg, self.exchange_module)
                self.sender.send_pyobj(exchange)
                self.logger.debug("%s receive exchange %s" % (self, exchange.value))

    def stop(self):
        """"""
        self.logger.debug("%s stop request" % self)
        super(ThreadedClient, self).stop()

    def send(self, exchange):
        """Use connector to send exchange

        It is up to the connector to manage the thread protection.
        """
        if exchange.broadcast:
            for _c in self.connections:
                if _c._name == exchange.origin:
                    _c.send(exchange)
                    self.logger.debug("%s use broadcast send exchange %s to %s" % (self, exchange.value, exchange.destination))
        else:
            for _c in self.connections:
                if _c._name in exchange.destination:
                    _c.send(exchange)
                    self.logger.debug("%s send exchange %s to %s" % (self, exchange.value, exchange.destination))
