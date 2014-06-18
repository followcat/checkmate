import sys
import time

import PyTango

import taurus.qt.qtgui.application
import taurus.qt.qtgui.button
import taurus.qt.qtgui.panel


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

    def delete_device(self):
        app.exit(0)

    def PBAC(self):
        button = get_button('ButtonAC')
        button.click()

    def PBRL(self):
        button = get_button('ButtonRL')
        button.click()

    def PBPP(self):
        button = get_button('ButtonPP')
        button.click()

    def ButtonAC(self):
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AC', _R)

    def ButtonRL(self):
        self.c3_dev.command_inout_asynch('RL')

    def ButtonPP(self):
        self.c1_dev.command_inout_asynch('PP')

    def ARE(self):
        _R = ['AT1', 'NORM']
        self.c1_dev.command_inout_asynch('AP', _R)

    def PA(self):
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
                'ButtonAC': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'ButtonRL': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'ButtonPP': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'ARE': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'PA': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'DR': [[PyTango.DevVoid], [PyTango.DevVoid]],
                'DA': [[PyTango.DevVoid], [PyTango.DevVoid]]
               }
    attr_list = {
                }

buttons = {}
model = 'sys/component_2/C2'
commands = ['ButtonAC', 'ButtonRL', 'ButtonPP']

def create_button(command, model=model):
    button = taurus.qt.qtgui.button.TaurusCommandButton(command=command)
    button.setModel(model)
    buttons[command] = button

def get_button(command):
    return buttons[command]

app = taurus.qt.qtgui.application.TaurusApplication(['Component_2'])
def start_taurus_app():
    for command in commands:
        create_button(command)
    panel = taurus.qt.qtgui.panel.TaurusCommandsForm()
    panel.setModel(model)
    def command_filter(command):
        return command.cmd_name in commands
    panel.setViewFilters([command_filter])
    #do Not show while running nose plugin
    #panel.show()
    app.exec_()

if __name__ == '__main__':
    py = PyTango.Util(['component_2', 'C2'])
    py.add_class(C2Interface, Component_2, 'Component_2')
    U = PyTango.Util.instance()
    U.server_init()
    #wait for server initializing completed
    time.sleep(2)
    start_taurus_app()
    U.server_run()

