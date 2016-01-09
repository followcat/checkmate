# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

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
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub.Type == zmq.DEALER, connector.socket_sub == None
        (True, True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c2, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub == None, connector.socket_sub.TYPE == zmq.SUB
        (True, True, True)
        >>> connector.close()

        >>> connector = checkmate.runtime._pyzmq.Connector(c3, c)
        >>> connector.initialize()
        >>> connector.socket_dealer_in.TYPE == zmq.DEALER, connector.socket_pub == None, connector.socket_sub.TYPE == zmq.SUB
        (True, True, True)
        >>> connector.close()

        >>> c.close()
    """
    def __init__(self, component, communication=None, is_reading=True):
        super(Connector, self).__init__(component, communication=communication, is_reading=is_reading)
        self._name = component.name
        self.is_reading = is_reading
        self.broadcast_map = component.broadcast_map
        self.is_publish = component.is_publish

        self.socket_pub = None
        self.socket_sub = None
        self.socket_dealer_in = None
        self.socket_dealer_out = None

        self.zmq_context = zmq.Context.instance()
        self._routerport = self.communication.get_routerport()
        self._broadcast_routerport = self.communication.get_broadcast_routerport()
        self._publishport = self.communication.get_publishport()

    def initialize(self):
        super(Connector, self).initialize()
        if self.is_publish:
            self.socket_pub = self.open_router_socket(zmq.DEALER, self._broadcast_routerport)
        if self.broadcast_map:
            self.socket_sub = self.open_router_socket(zmq.SUB, self._publishport)
            for _cname in self.broadcast_map.values():
                self.socket_sub.setsockopt(zmq.SUBSCRIBE, _cname.encode())
        self.socket_dealer_in = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_in.setsockopt(zmq.IDENTITY, self._name.encode())
        self.socket_dealer_out = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_in.connect("tcp://127.0.0.1:%i" % self._routerport)
        self.socket_dealer_out.connect("tcp://127.0.0.1:%i" % self._routerport)

    def open_router_socket(self, mode, port):
        new_socket = self.zmq_context.socket(mode)
        new_socket.connect("tcp://127.0.0.1:%i" % port)
        return new_socket

    def open(self):
        """"""

    def close(self):
        if self.socket_pub:
            self.socket_pub.close()
        if self.socket_sub:
            self.socket_sub.close()
        self.socket_dealer_in.close()
        self.socket_dealer_out.close()

    def send(self, exchange):
        """"""
        if exchange.broadcast:
            self.socket_pub.send_multipart([exchange.origin.encode(), self.communication.encoder.encode(exchange)])
        else:
            self.socket_dealer_out.send_multipart([exchange.destination[0].encode(), self.communication.encoder.encode(exchange)])


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
        >>> simulated_transition = r.application.components['C2'].state_machine.transitions[0]
        >>> o = c2_stub.simulate(simulated_transition)
        >>> c1_stub.context.state_machine.transitions[0].is_matching_incoming(o)
        True
        >>> c1_stub.validate(c1_stub.context.state_machine.transitions[0])
        True
        >>> time.sleep(1)
        >>> r.stop_test()
    """
    connector_class = Connector

    def __init__(self, component=None):
        """"""
        super(Communication, self).__init__(component)
        self.logger = logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize" % self)
        self.encoder = checkmate.runtime.communication.Encoder()
        self.router = checkmate.runtime.communication.Router(self.encoder)

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.router.start()

    def close(self):
        self.router.stop()
        self.logger.info("%s close" % self)

    def get_routerport(self):
        return self.router._routerport

    def get_broadcast_routerport(self):
        return self.router._broadcast_routerport

    def get_publishport(self):
        return self.router._publishport
