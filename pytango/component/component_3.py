import sys
import time

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
        
        self.subscribe_event_done = False

    def subscribe_event_run(self):
        self.c1_dev.subscribe_event('PA', PyTango.EventType.CHANGE_EVENT, self.PA_callback)
        self.subscribe_event_done = True

    def toggle(self):
        self.attr_c_state = not self.attr_c_state

    def RE(self):
        if self.attr_c_state == False:
            self.toggle()

    def RL(self):
        if self.attr_c_state == True:
            self.toggle()
            self.c2_dev.DR()

    def PA_callback(self, *args):
        if self.subscribe_event_done:
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
                'RL': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }


def event_loop():
    pytango_util = PyTango.Util.instance()
    for each in pytango_util.get_device_list_by_class('Component_3'):
        if hasattr(each, 'subscribe_event_done') and not each.subscribe_event_done:
            try:
                each.subscribe_event_run()
            except:
                continue
        else:
            time.sleep(1)


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C3Interface, Component_3, 'Component_3')
    U = PyTango.Util.instance()
    U.server_set_event_loop(event_loop)
    U.server_init()
    U.server_run()

