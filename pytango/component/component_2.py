import sys
import time

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
        self.user_dev = PyTango.DeviceProxy('sys/user/USER')
        
        self.is_sub = False

    def subscribe_event_run(self):
        self.c1_dev.subscribe_event('PA', PyTango.EventType.CHANGE_EVENT, self.PA_callback)
        self.is_sub = True

    def PBAC(self):
        #Execute asynchronously in case of nested called caused infinitely wait
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AC', _R)

    def PBRL(self):
        self.c3_dev.command_inout_asynch('RL')

    def PBPP(self):
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('PP', _R)

    def ARE(self):
        #Execute asynchronously in case of nested called caused infinitely wait
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AP', _R)

    def PA_callback(self, *args):
        if self.is_sub:
            self.user_dev.VOPA()

    def DA(self):
        self.user_dev.VODA()

    def DR(self):
        self.user_dev.VODR()


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
                'DR': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'DA': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }


def event_loop():
    pytango_util = PyTango.Util.instance()
    for each in pytango_util.get_device_list_by_class('Component_2'):
        if hasattr(each, 'is_sub') and not each.is_sub:
            each.subscribe_event_run()
        else:
            time.sleep(1)


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C2Interface, Component_2, 'Component_2')
    U = PyTango.Util.instance()
    U.server_set_event_loop(event_loop)
    U.server_init()
    U.server_run()

