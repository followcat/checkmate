import os
import sys
import time
import shlex
import pickle
import random
import threading

import zmq
import PyTango

import checkmate.runtime.encoder
import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


def add_device_service(services, component):
    publishs = component.publish_exchange
    subscribes = component.subscribe_exchange
    broadcast_map = component.broadcast_map

    d = {}
    code = """
        \nimport time
        \n
        \nimport PyTango
        \ndef __init__(self, *args):
        \n    super(self.__class__, self).__init__(*args)
        \n    self.is_sub = False"""
    for _publish in publishs:
        code += """
        \n    self.attr_%(pub)s_read = False
        \n    self.set_change_event('%(pub)s', True, False)""" % {'pub': _publish}

    code += """
        \ndef subscribe_event_run(self):"""
    for _subscribe in subscribes:
        component_name = broadcast_map[_subscribe]
        device_name = '/'.join(['sys', 'component_' + component_name.lstrip('C'), component_name])
        code += """
        \n    self.dev_%(name)s = PyTango.DeviceProxy('%(device)s')
        \n    self.dev_%(name)s.subscribe_event('%(sub)s', PyTango.EventType.CHANGE_EVENT, self.%(sub)s, stateless=False)""" % {'sub': _subscribe, 'name': component_name, 'device': device_name}
    code += """
        \n    self.is_sub = True
        \n    pass"""

    for _service in services:
        name = _service[0]
        if name not in publishs and name not in subscribes:
            code += """
                \ndef %(name)s(self, param=None):
                \n    self.send(('%(name)s', param))""" % {'name': name}

    for _subscribe in subscribes:
        component_name = broadcast_map[_subscribe]
        code += """
            \ndef %(sub)s(self, *args):
            \n    if self.is_sub:
            \n        self.send(('%(sub)s', None))""" % {'sub': _subscribe}

    for _publish in publishs:
        code += """
            \n
            \ndef read_%(pub)s(self, attr):
            \n    attr.set_value(self.attr_%(pub)s_read)
            \n
            \ndef write_%(pub)s(self, attr):
            \n    self.attr_%(pub)s_read = attr.get_write_value()
            \n    self.push_change_event('%(pub)s', self.attr_%(pub)s_read)""" % {'pub': _publish}

    exec(code, d)
    return d


def add_device_interface(services, component):
    publishs = component.publish_exchange
    subscribes = component.subscribe_exchange
    command = {}
    for _service in services:
        name = _service[0]
        args = _service[1]
        if name in publishs or name in subscribes:
            continue
        if args is not None:
            _type = switch(type(args[0]))
            command[name] = [[_type], [PyTango.DevVoid]]
        else:
            command[name] = [[PyTango.DevVoid], [PyTango.DevVoid]]
    attribute = {}
    for _publish in publishs:
        attribute[_publish] = [[PyTango.DevBoolean, PyTango.SCALAR, PyTango.READ_WRITE]]
    return {'cmd_list': command, 'attr_list': attribute}


def switch(_type=None):
    try:
        return {str:      PyTango.DevVarStringArray,
                int:      PyTango.DevVarLongArray,
                float:    PyTango.DevVarFloatArray,
                bool:     PyTango.DevVarBooleanArray,
               }[_type]
    except KeyError:
        return PyTango.DevVoid


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self, event):
        super(Registry, self).__init__()
        self.event = event
        self.pytango_util = PyTango.Util.instance()

    def event_loop(self):
        for _device in self.pytango_util.get_device_list('*'):
            if hasattr(_device, 'is_sub') and not _device.is_sub:
                try:
                    _device.subscribe_event_run()
                except:
                    continue
            else:
                time.sleep(checkmate.timeout_manager.PYTANGO_REGISTRY_SEC)
        if self.check_for_stop():
            dserver = self.pytango_util.get_dserver_device()
            dserver.kill()
            time.sleep(checkmate.timeout_manager.PYTANGO_REGISTRY_SEC)
            sys.exit(0)

    def run(self):
        self.pytango_util.server_init()
        self.event.set()
        self.pytango_util.server_set_event_loop(self.event_loop)
        self.pytango_util.server_run()


class Device(PyTango.Device_4Impl):
    def __init__(self, _class, name):
        PyTango.Device_4Impl.__init__(self, _class, name)
        self.init_device()

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.zmq_context = zmq.Context.instance()
        self.incoming = []
        self.socket = self.zmq_context.socket(zmq.PUSH)
        self.socket.connect("tcp://127.0.0.1:%i" % self._initport)

    def send(self, exchange):
        dump = pickle.dumps(exchange)
        self.socket.send(dump)


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


class Connector(checkmate.runtime.communication.Connector):
    def __init__(self, component, communication=None, is_server=False, is_broadcast=False):
        super().__init__(component, communication, is_server=is_server, is_broadcast=is_broadcast)
        self.device_name = '/'.join(['sys', type(self.component).__module__.split(os.extsep)[-1], self.component.name])
        if (self.is_server and not self.is_broadcast) or (not self.is_server and self.is_broadcast):
            self.device_class = type(component.name + 'Device', (Device,), add_device_service(component.services, self.component))
            self.interface_class = type(component.name + 'Interface', (DeviceInterface,), add_device_interface(component.services, self.component))
            self.device_name = self.communication.create_tango_device(self.device_class.__name__, self.component.name, type(self.component).__module__.split(os.extsep)[-1])
        self._name = component.name
        self.zmq_context = zmq.Context.instance()

    def initialize(self):
        if (self.is_server and not self.is_broadcast) or (not self.is_server and self.is_broadcast):
            self.socket = self.zmq_context.socket(zmq.PULL)
            self.port = self.socket.bind_to_random_port("tcp://127.0.0.1")
            setattr(self.device_class, '_initport', self.port)
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

    def send(self, exchange):
        if exchange.broadcast:
            setattr(self.device_client, exchange.action, False)
        else:
            attr = exchange.get_partition_attr()
            param = None
            if attr:
                param_type = switch(type(attr[0]))
                param = PyTango.DeviceData()
                param.insert(param_type, attr)
            call = getattr(self.device_client, exchange.action)
            call(param)


class Communication(checkmate.runtime.communication.Communication):
    connector_class = Connector

    def __init__(self, component=None):
        super(Communication, self).__init__(component)
        self.tango_database = PyTango.Database()
        if component is None:
            self.device_family = 'communication'
            self.server_name = self.create_tango_server('S%d' % (random.randint(0, 1000)))
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
