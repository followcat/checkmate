import logging

import zmq

import checkmate.timeout_manager
import checkmate.runtime.communication


class Connector(checkmate.runtime.communication.Connector):
    """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> a = sample_app.application.TestData()
        >>> c = checkmate.runtime._pyzmq.Communication()
        >>> c.initialize()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c3 = a.components['C3']
        >>> connector = checkmate.runtime._pyzmq.Connector(c1, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c2, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c3, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER
        True
        >>> connector.socket_sub.TYPE == zmq.SUB
        True
        >>> connector.close()

        >>> c.close()
    """
    def __init__(self, component, communication=None, is_reading=True):
        super(Connector, self).__init__(component,
            communication=communication, is_reading=is_reading)

    def initialize(self):
        super(Connector, self).initialize()

    def open(self):
        """"""

    def close(self):
        super(Connector, self).close()

    def send(self, exchange):
        """"""
        super(Connector, self).send(exchange)


class Communication(checkmate.runtime.communication.Communication):
    """
        >>> import time
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime
        >>> import checkmate.component
        >>> import sample_app.application
        >>> a = sample_app.application.TestData
        >>> c = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(a, c, True)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> c2_stub = r.runtime_components['C2']
        >>> c1_stub = r.runtime_components['C1']
        >>> c2 = r.application.components['C2']
        >>> simulated_transition = c2.state_machine.transitions[0]
        >>> o = c2_stub.simulate(simulated_transition)
        >>> t = c1_stub.context.state_machine.transitions[0]
        >>> t.is_matching_incoming(o)
        True
        >>> c1_stub.validate(t)
        True
        >>> time.sleep(1)
        >>> r.stop_test()
    """
    connector_class = Connector

    def __init__(self, component=None):
        """"""
        super(Communication, self).__init__(component)
        self.logger = \
            logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize" % self)

    def initialize(self):
        super(Communication, self).initialize()

    def start(self):
        super(Communication, self).start()

    def close(self):
        super(Communication, self).close()
        self.logger.info("%s close" % self)

    def connector_factory(self, component, is_reading=True):
        return self.connector_class(component, self, is_reading=is_reading)
