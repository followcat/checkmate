import sys

import PyTango

class Component_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Component_1, self).__init__(_class, name)
        Component_1.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.attr_a_state = True

    def AC(self):
        self.attr_a_state = not self.attr_a_state

    def read_a_state(self, attr):
        attr.set_value(self.attr_a_state)


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
 

    cmd_list = {'AC': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {'a_state': [[PyTango.ArgType.DevBoolean,
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ],
                              {
                              'Polling period': "100",
                              }]
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C1Interface, Component_1, 'Component_1')
    U = PyTango.Util.instance()
    U.server_init()
    print(U.get_device_by_name('sys/component_1/C1').get_device_class())
    U.server_run()

