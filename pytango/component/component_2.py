# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys

import PyTango


class Component_2(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Component_2, self).__init__(_class, name)
        Component_2.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.c1_dev = PyTango.DeviceProxy('sys/component_1/C1')
        self.c3_dev = PyTango.DeviceProxy('sys/component_3/C3')

    def PBAC(self):
        #Execute asynchronously in case of nested calls cause
        #infinitely wait
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AC', _R)

    def PBRL(self):
        self.c3_dev.command_inout_asynch('RL')

    def PBPP(self):
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('PP', _R)

    def ARE(self):
        #Execute asynchronously in case of nested calls cause
        #infinitely wait
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AP', _R)

    def PA(self):
        pass

    def DA(self):
        pass

    def DR(self):
        pass


class C2Interface(PyTango.DeviceClass):
    def dyn_attr(self, dev_list):
        """"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
 

    cmd_list = {'PBAC': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PBRL': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PBPP': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'ARE': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PA': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'DR': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'DA': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C2Interface, Component_2, 'Component_2')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

