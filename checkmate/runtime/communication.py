import queue
import logging
import multiprocessing

import checkmate.timeout_manager
import checkmate.runtime._threading


class Encoder(object):
    """"""
    def __init__(self, component):
        self.component = component

    def encode(self, exchange):
        return exchange

    def decode(self, message):
        return message


class Device(object):
    def __init__(self, component, communication=None, is_reading=False):
        self.component = component

    def initialize(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def send(self, exchange):
        pass


class Connector(object):
    """"""
    device_class = Device
    encoder_class = Encoder

    def __init__(self, component=None, communication=None, queue=None,
                 is_reading=False):
        self.queue = queue
        self.device = None
        self.encoder = self.encoder_class(component)
        self.component = component
        self.is_reading = is_reading
        self.communication = communication

    def initialize(self):
        """"""
        self.device = self.device_class(self.component, self.communication,
                        self.is_reading)
        setattr(self.device, 'connector', self)
        self.device.initialize()

    def open(self):
        """"""
        self.device.start()

    def inbound(self, *message):
        self.queue.put(self.encoder.decode(*message))

    def send(self, exchange):
        """"""
        self.device.send(self.encoder.encode(exchange))

    def close(self):
        """"""
        self.device.stop()


class ConnectorProcess(Connector, checkmate.runtime._threading.Process):
    """"""
    def __init__(self, component=None, communication=None, queue=None,
                 is_reading=False):
        super().__init__(component, communication, queue, is_reading)
        checkmate.runtime._threading.Process.__init__(self, component.name)
        self.send_queue = multiprocessing.Queue()

    def initialize(self):
        pass

    def open(self):
        self.start()

    def run(self):
        self.device = self.device_class(self.component, self.communication)
        self.device.start()
        setattr(self.device, 'connector', self)
        timeout_value = checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC
        while True:
            if self.check_for_stop():
                break
            try:
                exchange = self.send_queue.get(timeout=timeout_value)
                message = self.encoder.encode(exchange)
                self.device.send(message)
            except queue.Empty:
                pass

    def send(self, exchange):
        self.send_queue.put(exchange)
 
    def close(self):
        checkmate.runtime._threading.Process.stop(self)


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
