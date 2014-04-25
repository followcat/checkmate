import pytango.component.component_1
import pytango.checkmate.runtime.communication


class Device_1(pytango.checkmate.runtime.communication.Device):
    services = ('AC', 'AP', 'PP')

pytango.checkmate.runtime.communication.add_device_service(Device_1)


class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_1
    interface_class = pytango.component.component_1.C1Interface

