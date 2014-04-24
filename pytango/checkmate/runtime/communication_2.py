import PyTango

import pytango.component.component_2
import pytango.checkmate.runtime.communication


class Device_2(pytango.checkmate.runtime.communication.Device):
    services = ('ARE', 'PA', 'DA', 'DR')

d = {}
for name in Device_2.services:
    code = """def %s(self):
    self.incoming.append('%s')
    """ %(name, name)
    exec(code, d)
    setattr(Device_2, name, d[name])


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_2
    interface_class = pytango.component.component_2.C2Interface

