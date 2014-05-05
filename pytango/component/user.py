import sys

import PyTango


class User(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        super(User, self).__init__(_class, name)
        User.init_device(self)
        self.received_exchange = []

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.c2_dev = PyTango.DeviceProxy('sys/component_2/C2')

    def VODA(self):
        pass

    def VODR(self):
        pass

    def VOPA(self):
        pass


class USERInterface(PyTango.DeviceClass):
    def dyn_attr(self, dev_list):
        """"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
 

    cmd_list = {'VODA': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'VODR': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'VOPA': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(USERInterface, User, 'USER')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

