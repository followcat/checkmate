import PyTango

import pytango.component.component_3
import pytango.checkmate.runtime.communication


class Device_3(pytango.checkmate.runtime.communication.Device):
    services = ('RE', 'RL', 'PA')

pytango.checkmate.runtime.communication.add_device_service(Device_3)


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_3
    interface_class = pytango.component.component_3.C3Interface

