# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys

import PyTango

class Device_3(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Device_3, self).__init__(_class, name)
        Device_3.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)

    def ARE(self):
        pass

    def RL(self):
        pass

    def PA(self):
        pass


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
    py = PyTango.Util(sys.argv)
    py.add_class(C3Interface, Device_3, 'Device_3')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

