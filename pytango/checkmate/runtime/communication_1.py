import sys
import shlex

import PyTango

import checkmate.runtime.communication
import checkmate.runtime._threading

import sample_app.exchanges

import pytango.component_1.component


class Device_1(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        Device_1.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []

    def AC(self):
        exchange = sample_app.exchanges.AC()
        self.incoming.append(exchange)

    def AP(self):
        exchange = sample_app.exchanges.AP()
        self.incoming.append(exchange)

    def PP(self):
        exchange = sample_app.exchanges.PP()
        self.incoming.append(exchange)


class Connector(checkmate.runtime.communication.Connector):
    def __init__(self, component):
        super(Connector, self).__init__(component)

    def open(self):
        self.device_client = PyTango.DeviceProxy('sys/component/C1')
        self.device_server = self.registry.get_device_by_name('sys/component/C1')

    def receive(self):
        try:
            return self.device_server.incoming.pop(0)
        except:
            pass

    def send(self, destination, exchange):
        if exchange.action == 'AC':
            self.device_client.AC()
        elif exchange.action == 'AP':
            self.device_client.AP()
        elif exchange.action == 'PP':
            self.device_client.PP()


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
        pytango_server = PyTango.Util(shlex.split(__file__ + ' C1'))
        self.connector = Connector
        pytango_server.add_class(pytango.component_1.component.C1Interface, Device_1, 'Device_1')
        self.pytango_util = PyTango.Util.instance()
        self.connector.registry = self.pytango_util

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.registry = Registry(self.pytango_util)
        self.registry.start()

    def close(self):
        self.registry.stop()
        self.pytango_util.unregister_server()

