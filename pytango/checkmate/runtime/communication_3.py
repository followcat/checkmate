import sys
import shlex

import PyTango

import checkmate.runtime.communication
import checkmate.runtime._threading

import sample_app.exchanges

import pytango.component_3.component


class Device_3(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        Device_3.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []

    def RE(self):
        exchange = sample_app.exchanges.RE()
        self.incoming.append(exchange)

    def RL(self):
        exchange = sample_app.exchanges.RL()
        self.incoming.append(exchange)

    def PA(self):
        exchange = sample_app.exchanges.PA()
        self.incoming.append(exchange)


class Connector(checkmate.runtime.communication.Connector):
    def __init__(self, component):
        super(Connector, self).__init__(component)

    def open(self):
        self.device_client = PyTango.DeviceProxy('sys/component/C3')
        self.device_server = self.registry.get_device_by_name('sys/component/C3')

    def receive(self):
        try:
            return self.device_server.incoming.pop(0)
        except:
            pass

    def send(self, destination, exchange):
        if exchange.action == 'RE':
            self.device_client.RE()
        elif exchange.action == 'RL':
            self.device_client.RL()
        elif exchange.action == 'PA':
            self.device_client.PA()


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self, pytango_util):
        super(Registry, self).__init__()
        self.pytango_util = pytango_util

    def check_for_shutdown(self):
        if self.check_for_stop():
            sys.exit(0)
    
    def run(self):
        self.pytango_util.server_init()
        self.pytango_util.server_set_event_loop(self.check_for_shutdown)
        self.pytango_util.server_run()


class Communication(checkmate.runtime.communication.Communication):
    def __init__(self):
        super(Communication, self).__init__()
        pytango_server = PyTango.Util(shlex.split(__file__ + ' C3'))
        self.connector = Connector
        pytango_server.add_class(pytango.component_3.component.C3Interface, Device_3, 'Device_3')
        self.pytango_util = PyTango.Util.instance()
        self.connector.registry = self.pytango_util

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        #self.registry = Registry(self.pytango_util)
        #self.registry.start()

    def close(self):
        #self.registry.stop()
        #self.pytango_util.unregister_server()
        pass

