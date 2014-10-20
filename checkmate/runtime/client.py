import time
import logging
import collections

import zmq
import zope.interface

import checkmate.logger
import checkmate.timeout_manager
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
        self.return_code_list = collections.deque()

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
    def __init__(self, component, exchange_deque):
        super(ThreadedClient, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.name = component.name
        self.component = component
        self.exchange_deque = exchange_deque
        self.return_code_list = collections.deque()
        self.unprocess_list = collections.deque()

        self.connections = []
        self.zmq_context = zmq.Context.instance()
        self.poller = Poller()
        self.logger.debug("%s initial" % self)

    def add_connector(self, connector):
        self.connections.append(connector)

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
            if hasattr(_c, 'socket_out') and _c.socket_out is not None and _c.socket_out.TYPE == zmq.DEALER:
                self.poller.register(_c.socket_out, zmq.POLLIN)
        super(ThreadedClient, self).start()

    @checkmate.timeout_manager.WaitOnFalse(0.1, 100)
    def process_return_code(self):
        if not self.unprocess_list:
            return True
        if not self.return_code_list:
            return False
        unprocess = self.unprocess_list[0]
        incoming = self.return_code_list[0][0]
        return_code = self.return_code_list[0][1]
        if incoming.action == unprocess[1]:
            if incoming.broadcast:
                self.return_code_list.popleft()
                self.unprocess_list.popleft()
                return True
            else:
                for _c in self.connections:
                    if _c.socket_in and _c.socket_in.IDENTITY == unprocess[2]:
                        _c.socket_in.send_multipart([return_code.destination[0].encode(), checkmate.runtime.encoder.encode(return_code)])
                self.return_code_list.popleft()
                self.unprocess_list.popleft()
                return True
        return False

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                for _c in self.connections:
                    _c.close()
                self.logger.debug("%s stop" % self)
                break
            if self.unprocess_list:
                continue
            socks = dict(self.poller.poll(checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC))
            for _s in socks:
                msg = _s.recv_multipart()
                exchange = msg[-1]
                exchange = checkmate.runtime.encoder.decode(exchange, self.exchange_module)
                if len(msg) == 2:
                    self.unprocess_list.append([msg[0], exchange.action, _s.IDENTITY])
                    self.exchange_deque.append(exchange)
                    self.process_return_code()
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
