import sys
import shlex

import zope.component

import PyTango

import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.communication

import sample_app.exchanges

import pytango.component_1.component
import pytango.checkmate.runtime.communication


class Device_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        Device_1.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []

    def AC(self):
        self.incoming.append('AC')

    def AP(self):
        self.incoming.append('AP')

    def PP(self):
        self.incoming.append('PP')


class Encoder(object):
    def encode(self, exchange):
        return exchange.action
        if exchange.action == 'AC':
            self.device_client.AC()
        elif exchange.action == 'AP':
            self.device_client.AP()
        elif exchange.action == 'PP':
            self.device_client.PP()

    def decode(self, message):
        if message == 'AC':
            return sample_app.exchanges.AC()
        elif message == 'AP':
            return sample_app.exchanges.AP()
        elif message == 'PP':
            return sample_app.exchanges.PP()


class Connector(checkmate.runtime.communication.Connector):
    communication = pytango.checkmate.runtime.communication.Communication

    def __init__(self, component):
        super(Connector, self).__init__(component)
        _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
        if type(_communication) == self.communication:
            _communication.pytango_server.add_class(pytango.component_1.component.C1Interface, Device_1, 'Device_1')
        self.encoder = Encoder()

    def open(self):
        self.registry = PyTango.Util.instance()
        self.device_client = PyTango.DeviceProxy('sys/component/' + self.component.name)
        self.device_server = self.registry.get_device_by_name('sys/component/' + self.component.name)

    def receive(self):
        try:
            return self.encoder.decode(self.device_server.incoming.pop(0))
        except:
            pass

    def send(self, destination, exchange):
        call = getattr(self.device_client, self.encoder.encode(exchange))
        call()

