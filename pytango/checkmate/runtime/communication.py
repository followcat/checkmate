import os
import sys
import shlex
import random
import threading

import PyTango

import checkmate.runtime.communication
import checkmate.runtime._threading


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self, event):
        super(Registry, self).__init__()
        self.event = event
        self.pytango_util = PyTango.Util.instance()

    def check_for_shutdown(self):
        if self.check_for_stop():
            sys.exit(0)
    
    def run(self):
        self.pytango_util.server_init()
        self.event.set()
        self.pytango_util.server_set_event_loop(self.check_for_shutdown)
        self.pytango_util.server_run()


class Connector(checkmate.runtime.communication.Connector):
    """"""


class Communication(checkmate.runtime.communication.Communication):
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

