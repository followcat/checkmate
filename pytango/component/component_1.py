import sys

import PyTango


class Component_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(Component_1, self).__init__(_class, name)
        Component_1.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.attr_c_state = True
        self.c2_dev = PyTango.DeviceProxy('sys/component_2/C2')
        self.c3_dev = PyTango.DeviceProxy('sys/component_3/C3')

        self.attr_PA_read = False
        self.set_change_event('PA', True, False)

    def toggle(self):
        self.attr_c_state = not self.attr_c_state

    def AC(self, param):
        if self.attr_c_state == True:
            self.toggle()
            self.c3_dev.RE()
            self.c2_dev.ARE()

    def AP(self, param):
        self.c2_dev.DA()

    def PP(self, param):
        if self.attr_c_state == False:
            self.toggle()
            self.push_change_event('PA', self.attr_PA_read)

    def read_PA(self, attr):
        attr.set_value(self.attr_PA_read)


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

    cmd_list = {'AC': [[PyTango.DevVarStringArray], [PyTango.DevVoid]],
                'AP': [[PyTango.DevVarStringArray], [PyTango.DevVoid]],
                'PP': [[PyTango.DevVarStringArray], [PyTango.DevVoid]]
               }
    attr_list = {
                'PA': [[PyTango.DevBoolean, PyTango.SCALAR, PyTango.READ]],
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C1Interface, Component_1, 'Component_1')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

