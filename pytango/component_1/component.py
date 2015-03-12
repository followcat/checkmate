# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys

import PyTango

class Device_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Device_1, self).__init__(_class, name)
        Device_1.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)

    def AC(self):
        pass

    def AP(self):
        pass

    def PP(self):
        pass


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
               }
    attr_list = {
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C1Interface, Device_1, 'Device_1')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

