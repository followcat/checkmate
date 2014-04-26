import pytango.checkmate.runtime.communication


class Device_3(pytango.checkmate.runtime.communication.Device):
    """"""

class Interface(pytango.checkmate.runtime.communication.DeviceInterface):
    """"""

class Connector(pytango.checkmate.runtime.communication.Connector):
    device_class = Device_3
    interface_class = Interface

