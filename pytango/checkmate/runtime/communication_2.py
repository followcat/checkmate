import PyTango

import pytango.component.component_2
import pytango.checkmate.runtime.communication


class Device_2(pytango.checkmate.runtime.communication.Device):
    services = ('ARE', 'PA', 'DA', 'DR')

pytango.checkmate.runtime.communication.add_device_service(Device_2)


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_2
    interface_class = pytango.component.component_2.C2Interface

