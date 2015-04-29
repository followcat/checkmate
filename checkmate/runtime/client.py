# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import logging


class Client(object):
    """
        >>> import time
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.component
        >>> ac = sample_app.application.TestData
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> threaded = True
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> rc1 = r.runtime_components['C1']
        >>> rc2 = r.runtime_components['C2']
        >>> rc3 = r.runtime_components['C3']
        >>> are = sample_app.exchanges.AnotherReaction('ARE')
        >>> are._destination = ['C2']
        >>> rc1.client.send(are)
        >>> time.sleep(0.5)
        >>> are_t = [_t for _t in rc2.context.state_machine.transitions
        ...     if _t.incoming[0].code == 'ARE'][0]
        >>> rc2.context.validation_dict.collected_items[are_t][0].value
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
        >>> pa_t = [_t for _t in rc2.context.state_machine.transitions
        ...     if _t.incoming[0].code == 'PA'][0]
        >>> rc2.context.validation_dict.collected_items[pa_t][0].value
        'PA'
        >>> pa_t = [_t for _t in rc3.context.state_machine.transitions
        ...     if _t.incoming[0].code == 'PA'][0]
        >>> rc3.context.validation_dict.collected_items[pa_t][0].value
        'PA'
        >>> r.stop_test()
    """
    def __init__(self, component, exchange_queue):
        """"""
        self.name = component.name
        self.component = component
        self.exchange_queue = exchange_queue
        self.connections = []
        self.internal_connector = None
        self.external_connectors = {}
        self.logger = \
            logging.getLogger('checkmate.runtime.client.ThreadedClient')

    def initialize(self):
        """"""
        if self.internal_connector:
            self.internal_connector.initialize()
        for _connector in self.external_connectors.values():
            _connector.initialize()
        self.logger.debug("%s initial" % self)

    def start(self):
        """"""
        if self.internal_connector:
            self.internal_connector.open()
        for _connector in self.external_connectors.values():
            _connector.open()

    def stop(self):
        """"""
        if self.internal_connector:
            self.internal_connector.close()
        for _connector in self.external_connectors.values():
            _connector.close()
        self.logger.debug("%s stop" % self)

    def send(self, exchange):
        """Use connector to send exchange"""
        if self.internal_connector:
            self.internal_connector.send(exchange)
        try:
            self.external_connectors[exchange.communication].send(exchange)
        except KeyError:
            #nothing can be done for now
            pass
        self.logger.debug("%s send exchange %s to %s" %
            (self, exchange.value, exchange.destination))

    def receive(self, exchange):
        """"""
        self.exchange_queue.put(exchange)
        self.logger.debug("%s receive exchange %s" % (self, exchange.value))

