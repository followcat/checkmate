import PyTango

import pytango.component.component_3
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

class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_3
    interface_class = pytango.component.component_3.C3Interface

