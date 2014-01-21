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
    def __init__(self):
        super(Communication, self).__init__()
        self.server_name = self.create_tango_server()
        self.event = threading.Event()

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.pytango_server = PyTango.Util(shlex.split(__file__ + ' ' + self.server_name))

    def start(self):
        self.registry = Registry(self.event)
        self.registry.start()
        #wait for server initialized
        self.event.wait(timeout=2)

    def close(self):
        pytango_util = PyTango.Util.instance()
        pytango_util.unregister_server()
        self.delete_tango_device("dserver/communication/" + self.server_name)
        self.registry.stop()

    def create_tango_server(self):
        _server_name = "S%d" %(random.randint(0, 1000))
        db = PyTango.Database()
        comp = PyTango.DbDevInfo()
        comp._class = "DServer"
        comp.server = "communication/" + _server_name
        comp.name = "dserver/communication/" + _server_name
        db.add_device(comp)
        return _server_name

    def create_tango_device(self, component_class, component):
        db = PyTango.Database()
        comp = PyTango.DbDevInfo()
        comp._class = component_class
        comp.server = "communication/" + self.server_name
        comp.name = "sys/component/" + component
        db.add_device(comp)
        return comp.name

    def delete_tango_device(self, device_name):
        db = PyTango.Database()
        db.delete_device(device_name)

