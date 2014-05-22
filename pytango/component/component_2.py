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

    def ARE(self, param=''):
        #Execute asynchronously in case of nested called caused infinitely wait
        self.c1_dev.command_inout_asynch('AP', "R=pytango.checkmate.data_structure.ActionRequest(P=pytango.checkmate.data_structure.ActionPriority('NORM'), A=pytango.checkmate.data_structure.Attribute('AT1'))")

    def PA(self, param=''):
        pass

    def DA(self, param=''):
        pass

    def DR(self, param=''):
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
 

    cmd_list = {'ARE': [[PyTango.DevString], [PyTango.DevVoid]],
                'PA': [[PyTango.DevString], [PyTango.DevVoid]],
                'DR': [[PyTango.DevString], [PyTango.DevVoid]],
                'DA': [[PyTango.DevString], [PyTango.DevVoid]]
               }
    attr_list = {
                }


if __name__ == '__main__':
    py = PyTango.Util(sys.argv)
    py.add_class(C2Interface, Component_2, 'Component_2')
    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

