import sys
import shlex

import zope.component

import PyTango

import checkmate.runtime.registry
import checkmate.runtime._threading
import checkmate.runtime.communication

import sample_app.exchanges

import pytango.component_2.component
import pytango.checkmate.runtime.communication


class Device_2(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        Device_2.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []

    def ARE(self):
        self.incoming.append('ARE')

    def PA(self):
        self.incoming.append('PA')

    def DA(self):
        self.incoming.append('DA')


class Encoder(object):
    def encode(self, exchange):
        return exchange.action
        if exchange.action == 'ARE':
            self.device_client.ARE()
        elif exchange.action == 'PA':
            self.device_client.PA()
        elif exchange.action == 'DA':
            self.device_client.DA()

    def decode(self, message):
        if message == 'ARE':
            return sample_app.exchanges.ARE()
        elif message == 'PA':
            return sample_app.exchanges.PA()
        elif message == 'DA':
            return sample_app.exchanges.DA()


class Connector(checkmate.runtime.communication.Connector):
    communication = pytango.checkmate.runtime.communication.Communication

    def __init__(self, component):
        super(Connector, self).__init__(component)
        _communication = checkmate.runtime.registry.global_registry.getUtility(checkmate.runtime.interfaces.ICommunication)
        if type(_communication) == self.communication:
            _communication.pytango_server.add_class(pytango.component_2.component.C2Interface, Device_2, 'Device_2')
        self.encoder = Encoder()

    def open(self):
        self.registry = PyTango.Util.instance()
        self.device_client = PyTango.DeviceProxy('sys/component/C2')
        self.device_server = self.registry.get_device_by_name('sys/component/C2')

    def receive(self):
        try:
            return self.encoder.decode(self.device_server.incoming.pop(0))
        except:
            pass

    def send(self, destination, exchange):
        call = getattr(self.device_client, self.encoder.encode(exchange))
        call()

