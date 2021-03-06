# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys

import PyTango


class Component_3(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Component_3, self).__init__(_class, name)
        Component_3.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.attr_c_state = False
        self.c1_dev = PyTango.DeviceProxy('sys/component_1/C1')
        self.c2_dev = PyTango.DeviceProxy('sys/component_2/C2')

    def toggle(self):
        self.attr_c_state = not self.attr_c_state

    def RE(self):
        if self.attr_c_state == False:
            self.toggle()

    def RL(self):
        if self.attr_c_state == True:
            self.toggle()
            self.c2_dev.DR()

    def PA(self):
        if self.attr_c_state == False:
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
    py.add_class(C3Interface, Component_3, 'Component_3')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

