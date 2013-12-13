import sys

import PyTango

class Device_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Device_1, self).__init__(_class, name)
        Device_1.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.attr_c_state = True
        self.c2_dev = PyTango.DeviceProxy('sys/component/C2')
        self.c3_dev = PyTango.DeviceProxy('sys/component/C3')

    def toggle(self):
        self.attr_c_state = not self.attr_c_state

    def AC(self):
        if self.attr_c_state == True:
            self.toggle()
            self.c3_dev.RE()
            self.c2_dev.ARE()

    def AP(self):
        self.c2_dev.DA()

    def PP(self):
        if self.attr_c_state == False:
            self.toggle()
            self.c2_dev.PA()
            self.c3_dev.PA()


class C1Interface(PyTango.DeviceClass):
    def dyn_attr(self, dev_list):
        """"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
 

    cmd_list = {'AC': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'AP': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PP': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'toggle': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {'c_state': [[PyTango.ArgType.DevBoolean,
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ_WRITE],
                              {
                              'Polling period': "100",
                              }]
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C1Interface, Device_1, 'Device_1')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

