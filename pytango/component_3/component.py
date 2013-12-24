import sys

import PyTango
import pytango._database

class Device_3(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Device_3, self).__init__(_class, name)
        Device_3.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.attr_c_state = False
        self.c1_dev = PyTango.DeviceProxy('sys/component/C1')

    def toggle(self):
        self.attr_c_state = not self.attr_c_state

    def RE(self):
        if self.attr_c_state == False:
            self.toggle()

    def RL(self):
        self.c1_dev.PP()

    def PA(self):
        if self.attr_c_state == True:
            self.toggle()


class C3Interface(PyTango.DeviceClass):
    def dyn_attr(self, dev_list):
        """"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
 

    cmd_list = {'RE': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'RL': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PA': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }


if __name__ == '__main__':
    pytango._database.create_component_device('Device_3', 'C3')
    py = PyTango.Util(sys.argv)
    py.add_class(C3Interface, Device_3, 'Device_3')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

