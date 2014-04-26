import pytango.component.component_3
import pytango.checkmate.runtime.communication


class Device_3(pytango.checkmate.runtime.communication.Device):
    """"""

class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_3
    interface_class = pytango.component.component_3.C3Interface

