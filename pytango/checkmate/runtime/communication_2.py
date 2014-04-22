import PyTango

import pytango.component.component_2
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
    
    def DR(self):
        self.incoming.append('DR')

class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_2
    interface_class = pytango.component.component_2.C2Interface

