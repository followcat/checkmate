import os
import sys
import time
import shlex
import random
import threading

import PyTango

import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


SLEEP_WHEN_RUN_SEC = 0.001

def add_device_service(services):
    d = {}
    for name in services:
        code = """
def %s(self):
    self.incoming.append('%s')""" %(name, name)
        exec(code, d)
    return d

def add_device_interface(services):
    command = {}
    for name in services:
        command[name] = [[PyTango.DevVoid], [PyTango.DevVoid]]
    return {'cmd_list': command}


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self, event):
        super(Registry, self).__init__()
        self.event = event
        self.pytango_util = PyTango.Util.instance()

    def check_for_shutdown(self):
        time.sleep(1)
        if self.check_for_stop():
            sys.exit(0)
    
    def run(self):
        self.pytango_util.server_init()
        self.event.set()
        self.pytango_util.server_set_event_loop(self.check_for_shutdown)
        self.pytango_util.server_run()


class Device(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        self.init_device()

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.incoming = []


class DeviceInterface(PyTango.DeviceClass):
    cmd_list = {}
    attr_list = {}

    def dyn_attr(self, dev_list):
        """"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())


class Encoder(object):
    def encode(self, exchange):
        return exchange.action

    def decode(self, message):
        #cannot be imported before the application is created
        import pytango.checkmate.exchanges

        return getattr(pytango.checkmate.exchanges, message)()


class Connector(checkmate.runtime.communication.Connector):
    def __init__(self, component, communication=None, is_server=False):
        super().__init__(component, communication, is_server=is_server)
        self.device_name = '/'.join(['sys', type(self.component).__module__.split(os.extsep)[-1], self.component.name])
        if self.is_server:
            self.device_class = type(component.name + 'Device', (Device,), add_device_service(component.services))
            self.interface_class = type(component.name + 'Interface', (DeviceInterface,), add_device_interface(component.services))
            self.device_name = self.communication.create_tango_device(self.device_class.__name__, self.component.name, type(self.component).__module__.split(os.extsep)[-1])
        self.encoder = Encoder()
        self.receive_condition = threading.Condition()

    def initialize(self):
        if self.is_server:
            self.communication.pytango_server.add_class(self.interface_class, self.device_class, self.device_class.__name__)

    def open(self):
        @checkmate.timeout_manager.WaitOnException(timeout=10)
        def check():
            self.device_client.attribute_list_query()
        self.registry = PyTango.Util.instance()
        self.device_client = PyTango.DeviceProxy(self.device_name)
        check()
        if self.is_server:
            self.device_server = self.registry.get_device_by_name(self.device_name)

    def close(self):
        self.communication.delete_tango_device(self.device_name)

    def check_receive(self):
        try:
            return len(self.device_server.incoming) > 0
        except AttributeError:
            return False

    def receive(self):
        with self.receive_condition:
            if self.receive_condition.wait_for(self.check_receive, SLEEP_WHEN_RUN_SEC):
                return self.encoder.decode(self.device_server.incoming.pop(0))

    def send(self, destination, exchange):
        call = getattr(self.device_client, self.encoder.encode(exchange))
        call()


class Communication(checkmate.runtime.communication.Communication):
    connector_class = Connector

    def __init__(self, component=None):
        super(Communication, self).__init__(component)
        self.tango_database = PyTango.Database()
        if component is None:
            self.device_family = 'communication'
            self.server_name = self.create_tango_server('S%d' %(random.randint(0, 1000)))
        else:
            self.device_family = type(component).__module__.split(os.extsep)[-1]
            self.server_name = self.create_tango_server(component.name)
            _device_name = self.create_tango_device(component.__class__.__name__, component.name, self.device_family)

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.pytango_server = PyTango.Util(shlex.split(__file__ + ' ' + self.server_name))

    def start(self):
        self.event = threading.Event()
        self.registry = Registry(self.event)
        self.registry.start()
        #wait for server initialized
        self.event.wait(timeout=2)

    def close(self):
        pytango_util = PyTango.Util.instance()
        try:
            pytango_util.unregister_server()
        except PyTango.DevFailed as e:
            #Bypass any exception as no failure can be reported at this stage
            pass
        self.delete_tango_device('/'.join(('dserver', self.device_family, self.server_name)))
        self.registry.stop()

    def create_tango_server(self, server_name):
        comp = PyTango.DbDevInfo()
        comp._class = "DServer"
        comp.server = '/'.join((self.device_family, server_name))
        comp.name = '/'.join(('dserver', self.device_family, server_name))
        self.tango_database.add_device(comp)
        return server_name

    def create_tango_device(self, component_class, component, device_family):
        comp = PyTango.DbDevInfo()
        comp._class = component_class
        comp.server = '/'.join((self.device_family, self.server_name))
        comp.name = '/'.join(('sys', device_family, component))
        self.tango_database.add_device(comp)
        return comp.name

    def delete_tango_device(self, device_name):
        try:
            #Use a new database connection in case the existing one was shut down
            db = PyTango.Database()
            db.delete_device(device_name)
        except PyTango.DevFailed as e:
            pass
        except PyTango.ConnectionFailed as e:
            pass

