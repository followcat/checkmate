import logging

import zmq

import checkmate.logger
import checkmate.runtime._threading
import checkmate.runtime._zmq_wrapper


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
        >>> are = sample_app.exchanges.AnotherReaction('ARE')
        >>> are._destination = ['C2']
        >>> rc1.client.send(are)
        >>> time.sleep(0.5)
        >>> rc2.context.validation_list.all_items()[0].value
        'ARE'
        >>> rc2.reset()
        >>> rc3.reset()
        >>> pa = sample_app.exchanges.Pause('PA')
        >>> pa._origin = 'C1'
        >>> pa.broadcast
        True
        >>> rc1.client.send(pa)
        >>> time.sleep(0.5)
        >>> import time; time.sleep(1)
        >>> rc2.context.validation_list.all_items()[0].value
        'PA'
        >>> rc3.context.validation_list.all_items()[0].value
        'PA'
        >>> r.stop_test()
    """
    def __init__(self, component, exchange_queue):
        super(ThreadedClient, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime.client.ThreadedClient')
        self.name = component.name
        self.component = component
        self.exchange_queue = exchange_queue

        self.connections = []
        self.internal_connector = None
        self.external_connectors = {}
        self.logger.debug("%s initial" % self)
        self.poller = checkmate.runtime._zmq_wrapper.Poller()

    def set_exchange_module(self, exchange_module):
        self.exchange_module = exchange_module

    def initialize(self):
        """"""
        if self.internal_connector:
            self.internal_connector.initialize()
        for _connector in self.external_connectors.values():
            _connector.initialize()

    def start(self):
        if self.internal_connector and self.internal_connector.is_reading:
            if self.internal_connector.socket_sub:
                self.poller.register(self.internal_connector.socket_sub)
            self.poller.register(self.internal_connector.socket_dealer_in)
        for _connector in [_c for _c in self.external_connectors.values() if _c.is_reading]:
            if _connector.socket_sub:
                self.poller.register(_connector.socket_sub)
            self.poller.register(_connector.socket_dealer_in)
        if self.internal_connector:
            self.internal_connector.open()
        for _connector in self.external_connectors.values():
            _connector.open()
        super(ThreadedClient, self).start()

    def run(self):
        """"""
        self.logger.debug("%s startup" % self)
        while True:
            if self.check_for_stop():
                if self.internal_connector:
                    self.internal_connector.close()
                for _connector in self.external_connectors.values():
                    _connector.close()
                self.logger.debug("%s stop" % self)
                break
            socks = self.poller.poll_with_timeout()
            for _s in socks:
                if _s.TYPE == zmq.SUB:
                    _s.recv()
                exchange = _s.recv_pyobj()
                self.exchange_queue.put(exchange)
                self.logger.debug("%s receive exchange %s" % (self, exchange.value))

    def stop(self):
        """"""
        self.logger.debug("%s stop request" % self)
        super(ThreadedClient, self).stop()

    def send(self, exchange):
        """Use connector to send exchange

        It is up to the connector to manage the thread protection.
        """
        if self.internal_connector:
            self.internal_connector.send(exchange)
        for _name, _connector in self.external_connectors.items():
            _connector.send(exchange)
        self.logger.debug("%s send exchange %s to %s" % (self, exchange.value, exchange.destination))
