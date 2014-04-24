import PyTango

import pytango.component.component_3
import pytango.checkmate.runtime.communication


class Device_3(pytango.checkmate.runtime.communication.Device):
    services = ('RE', 'RL', 'PA')

d = {}
for name in Device_3.services:
    code = """def %s(self):
    self.incoming.append('%s')
    """ %(name, name)
    exec(code, d)
    setattr(Device_3, name, d[name])


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_3
    interface_class = pytango.component.component_3.C3Interface

