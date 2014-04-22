import PyTango

import pytango.component.component_1
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



class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_1
    interface_class = pytango.component.component_1.C1Interface

