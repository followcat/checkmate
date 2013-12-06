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
        if exchange.action == 'RE':
            self.device_client.RE()
        elif exchange.action == 'RL':
            self.device_client.RL()
        elif exchange.action == 'PA':
            self.device_client.PA()

    def decode(self, message):
        if message == 'RE':
            return sample_app.exchanges.RE()
        elif message == 'RL':
            return sample_app.exchanges.RL()
        elif message == 'PA':
            return sample_app.exchanges.PA()


class Connector(checkmate.runtime.communication.Connector):
    communication = pytango.checkmate.runtime.communication.Communication

    def __init__(self, component):
        super(Connector, self).__init__(component)
        _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
        if type(_communication) == self.communication:
            _communication.pytango_server.add_class(pytango.component_3.component.C3Interface, Device_3, 'Device_3')
        self.encoder = Encoder()

    def open(self):
        self.registry = PyTango.Util.instance()
        self.device_client = PyTango.DeviceProxy('sys/component/C3')
        self.device_server = self.registry.get_device_by_name('sys/component/C3')

    def receive(self):
        try:
            return self.encoder.decode(self.device_server.incoming.pop(0))
        except:
            pass

    def send(self, destination, exchange):
        call = getattr(self.device_client, self.encoder.encode(exchange))
        call()


