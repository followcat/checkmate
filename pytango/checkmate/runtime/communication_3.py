import sys
import shlex

import zope.component

import PyTango

import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.communication

import sample_app.exchanges

import pytango.component_3.component
import pytango.checkmate.runtime.communication


class Device_3(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        Device_3.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []

    def RE(self):
        self.incoming.append('RE')

    def RL(self):
        self.incoming.append('RL')

    def PA(self):
        self.incoming.append('PA')


class Encoder(object):
    def encode(self, exchange):
        return exchange.action

    def decode(self, message):
        if message == 'RE':
            return sample_app.exchanges.RE()
        elif message == 'RL':
            return sample_app.exchanges.RL()
        elif message == 'PA':
            return sample_app.exchanges.PA()


class Connector(checkmate.runtime.communication.Connector):
    communication = pytango.checkmate.runtime.communication.Communication

    def __init__(self, component, internal=False, is_server=False):
        super(Connector, self).__init__(component, internal=internal, is_server=is_server)
        self.device_name = 'sys/component/' + self.component.name
        if self.is_server:
            _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
            if type(_communication) == self.communication:
                self.device_name = _communication.create_tango_device('Device_3', self.component.name)
        self.encoder = Encoder()

    def initialize(self):
        if self.is_server:
            _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
            if type(_communication) == self.communication:
                _communication.pytango_server.add_class(pytango.component_3.component.C3Interface, Device_3, 'Device_3')

    def open(self):
        @checkmate.runtime.timeout_manager.WaitOnException(timeout=10)
        def check():
            self.device_client.attribute_list_query()
        self.registry = PyTango.Util.instance()
        self.device_client = PyTango.DeviceProxy(self.device_name)
        check()
        if self.is_server:
            self.device_server = self.registry.get_device_by_name(self.device_name)

    def close(self):
        _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
        _communication.delete_tango_device(self.device_name)

    def receive(self):
        try:
            return self.encoder.decode(self.device_server.incoming.pop(0))
        except:
            pass

    def send(self, destination, exchange):
        call = getattr(self.device_client, self.encoder.encode(exchange))
        call()

