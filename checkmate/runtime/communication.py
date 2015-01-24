import logging


class Encoder(object):
    """"""
    def encode(self, exchange):
        return exchange

    def decode(self, message):
        return message


class Connector(object):
    """"""
    def __init__(self, component=None, communication=None, queue=None,
                 is_reading=False):
        self.queue = queue
        self.encoder = Encoder()
        self.component = component
        self.communication = communication

    def initialize(self):
        """"""

    def open(self):
        """"""

    def inbound(self, *message):
        self.queue.put(self.encoder.decode(*message))

    def send(self, exchange):
        """"""

    def close(self):
        """"""


class Communication(object):
    """"""
    connector_class = Connector
    def __init__(self, component=None):
        """"""
        self.logger = \
            logging.getLogger('checkmate.runtime._pyzmq.Communication')

    def initialize(self):
        """"""
        self.logger.info("%s initialize" % self)

    def start(self):
        """"""

    def close(self):
        """"""
        self.logger.info("%s close" % self)

    def connector_factory(self, component, queue, is_reading=True):
        return self.connector_class(component, self, queue,
                    is_reading=is_reading)
