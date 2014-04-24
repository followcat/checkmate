import PyTango

import pytango.component.component_1
import pytango.checkmate.runtime.communication


class Device_1(pytango.checkmate.runtime.communication.Device):
    services = ('AC', 'AP', 'PP')

d = {}
for name in Device_1.services:
    code = """def %s(self):
    self.incoming.append('%s')
    """ %(name, name)
    exec(code, d)
    setattr(Device_1, name, d[name])


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_1
    interface_class = pytango.component.component_1.C1Interface

