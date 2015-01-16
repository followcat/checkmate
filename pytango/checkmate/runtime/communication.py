import os
import sys
import time
import shlex
import pickle
import random
import threading

import zmq
import PyTango

import checkmate.timeout_manager
import checkmate.runtime._threading
import checkmate.runtime.communication


def add_device_service(services, component):
    publishs = component.publish_exchange
    subscribes = component.subscribe_exchange
    broadcast_map = component.broadcast_map

    exchange_dict = {}
    d = {}
    code = """
        \nimport time
        \n
        \nimport PyTango
        \ndef __init__(self, *args):
        \n    super(self.__class__, self).__init__(*args)
        \n    self.subscribe_event_id_dict = {}
        \n    self.subscribe_event_done = False
        \n    self._name = '%s'""" % component.name
    for _publish in publishs:
        code += """
            \n    self.attr_%(pub)s_read = 1
            \n    self.%(pub)s_counter = 0
            \n    %(pub)s = self.get_device_attr().get_attr_by_name('%(pub)s')
            \n    %(pub)s.set_data_ready_event(True)""" % {'pub': _publish}

    for _subscribe in subscribes:
        component_name = broadcast_map[_subscribe]
        device_name = '/'.join(['sys', 'component_' +
                              component_name.lstrip('C'), component_name])
        code += """
            \n    self.dev_%(name)s = PyTango.DeviceProxy('%(device)s')""" % {
                'name': component_name, 'device': device_name}

    code += """
        \ndef subscribe_event_run(self):"""
    for _subscribe in subscribes:
        component_name = broadcast_map[_subscribe]
        code += """
            \n    id = self.dev_%(name)s.subscribe_event( \
                           '%(sub)s', \
                            PyTango.EventType.DATA_READY_EVENT, \
                            self.%(sub)s,\
                            stateless=False)
            \n    self.subscribe_event_id_dict[id] = self.dev_%(name)s""" % {
                'sub': _subscribe, 'name': component_name}
    code += """
        \n    self.subscribe_event_done = True
        \n    pass"""

    for _service in services:
        name = _service[0]
        exchange_dict[name] = ([type(_service[1]), _service[1].value])
        if name not in publishs and name not in subscribes:
            code += """
                \ndef %(name)s(self, param=[]):
                \n    self.send('%(name)s', param)""" % {'name': name}

    for _subscribe in subscribes:
        component_name = broadcast_map[_subscribe]
        code += """
            \ndef %(sub)s(self, *args):
            \n    if self.subscribe_event_done:
            \n        self.send(('%(sub)s', None))""" % {'sub': _subscribe}

    for _publish in publishs:
        code += """
            \n
            \ndef read_%(pub)s(self, attr):
            \n    attr.set_value(self.attr_%(pub)s_read)
            \n
            \ndef write_%(pub)s(self, attr):
            \n    self.attr_%(pub)s_read += 1
            \n    self.push_data_ready_event('%(pub)s', \
                      self.attr_%(pub)s_read)""" % {'pub': _publish}

    exec(code, d)
    d['exchange_dict'] = exchange_dict
    return d


def add_device_interface(services, component, encoder):
    publishs = component.publish_exchange
    subscribes = component.subscribe_exchange
    command = {}
    for _service in services:
        name = _service[0]
        args = encoder.get_partition_values(_service[1])
        if name in publishs or name in subscribes:
            continue
        if args:
            command[name] = [[PyTango.DevVarStringArray], [PyTango.DevVoid]]
        else:
            command[name] = [[PyTango.DevVoid], [PyTango.DevVoid]]
    attribute = {}
    for _publish in publishs:
        attribute[_publish] = \
            [[PyTango.DevBoolean, PyTango.SCALAR, PyTango.READ_WRITE]]
    return {'cmd_list': command, 'attr_list': attribute}


class Encoder(checkmate.runtime.communication.Encoder):
    def get_partition_values(self, partition, values_list=None):
        """
            >>> import pytango.checkmate.application
            >>> import pytango.checkmate.runtime.communication
            >>> ac = pytango.checkmate.exchanges.AC()
            >>> encoder = pytango.checkmate.runtime.communication.Encoder()
            >>> encoder.get_partition_values(ac)
            ['AT1', 'NORM']
        """
        if values_list is None:
            values_list = []
        for name in dir(partition):
            attr = getattr(partition, name)
            self.get_partition_values(attr, values_list)
            if attr.value is not None:
                values_list.append(attr.value)
        return values_list

    def _dump(self, exchange_type, exchange_value, param):
        partition = {}
        return (exchange_type, exchange_value, partition)

    def _load(self, data):
        exchange_type, exchange_value, exchange_partition = data
        return exchange_type(exchange_value, **exchange_partition)


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self, event):
        super(Registry, self).__init__()
        self.event = event
        self.pytango_util = PyTango.Util.instance()

    def event_loop(self):
        for _device in self.pytango_util.get_device_list('*'):
            if (hasattr(_device, 'subscribe_event_done') and
                    not _device.subscribe_event_done):
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
        self.socket_dealer_out = self.zmq_context.socket(zmq.DEALER)
        self.socket_dealer_out.connect("tcp://127.0.0.1:%i" % self._routerport)

    def send(self, code, param):
        exchange_type, exchange_value = self.exchange_dict[code]
        send_data = self.encoder.encode(exchange_type, exchange_value, param)
        self.socket_dealer_out.send_multipart([self._name.encode(), send_data])


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
    def __init__(self, component, communication=None, is_reading=True,
                 is_broadcast=False):
        super().__init__(component, communication, is_server=True,
            is_reading=is_reading, is_broadcast=is_broadcast)
        self.device_class = \
            type(component.name + 'Device', (Device,),
                add_device_service(component.services, self.component))
        self.interface_class = \
            type(component.name + 'Interface', (DeviceInterface,),
                add_device_interface(component.services,
                    self.component, self.communication.encoder))
        self.device_name = \
            self.communication.create_tango_device(
                self.device_class.__name__, self.component.name,
                type(self.component).__module__.split(os.extsep)[-1])
        self._name = component.name
        self.communication.comp_device[component.name] = self.device_name
        self._routerport = self.communication.get_routerport()
        self.zmq_context = zmq.Context.instance()

    def initialize(self):
        if self.is_server:
            self.socket_dealer_in = self.zmq_context.socket(zmq.DEALER)
            self.socket_dealer_out = self.zmq_context.socket(zmq.DEALER)
            self.socket_dealer_in.setsockopt(zmq.IDENTITY, self._name.encode())
            self.socket_dealer_in.connect("tcp://127.0.0.1:%i" %
                self._routerport)
            self.socket_dealer_out.connect("tcp://127.0.0.1:%i" %
                self._routerport)
            setattr(self.device_class, '_routerport', self._routerport)
            setattr(self.device_class, 'encoder', self.communication.encoder)
            self.communication.pytango_server.add_class(self.interface_class,
                self.device_class, self.device_class.__name__)

    def open(self):
        @checkmate.timeout_manager.WaitOnException(timeout=10)
        def check(dev_proxy):
            dev_proxy.attribute_list_query()
        for dev_name in list(self.communication.comp_device.values()):
            if dev_name != self.device_name:
                dev_proxy = self.communication.get_device_proxy(dev_name)
                check(dev_proxy)

    def close(self):
        self.communication.delete_tango_device(self.device_name)

    def send(self, exchange):
        if exchange.broadcast:
            self.socket_dealer_out.send(pickle.dumps([self.device_name,
                                            exchange]))
        else:
            attribute_values = \
                self.communication.encoder.get_partition_values(exchange)
            param = None
            if attribute_values:
                param_type = PyTango.DevVarStringArray
                param = PyTango.DeviceData()
                param.insert(param_type, attribute_values)
            for des in exchange.destination:
                device_proxy = self.communication.get_device_proxy(
                                   self.communication.comp_device[des])
                call = getattr(device_proxy, exchange.value)
                call(param)


class Communication(checkmate.runtime.communication.Communication):
    connector_class = Connector
    #dictionary to contain all component-device name pairs
    comp_device = {}

    def __init__(self, component=None):
        super(Communication, self).__init__(component)
        self.tango_database = PyTango.Database()
        if component is None:
            self.device_family = 'communication'
            self.server_name = \
                self.create_tango_server('S%d' % (random.randint(0, 1000)))
        else:
            self.device_family = \
                type(component).__module__.split(os.extsep)[-1]
            self.server_name = self.create_tango_server(component.name)
            _device_name = \
                self.create_tango_device(component.__class__.__name__,
                    component.name, self.device_family)
            self.comp_device[component.name] = _device_name
        self.encoder = Encoder()
        self.router = checkmate.runtime.communication.Router(self.encoder)
        self.dev_proxies = {}

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.pytango_server = \
            PyTango.Util(shlex.split(__file__ + ' ' + self.server_name))

    def get_routerport(self):
        return self.router._routerport

    def start(self):
        self.event = threading.Event()
        self.registry = Registry(self.event)
        self.registry.start()
        self.router.start()
        #wait for server initialized
        self.event.wait(timeout=2)

    def get_device_proxy(self, device_name):
        if device_name in list(self.dev_proxies.keys()):
            return self.dev_proxies[device_name]
        else:
            dev_proxy = PyTango.DeviceProxy(device_name)
            self.dev_proxies[device_name] = dev_proxy
            return dev_proxy

    def close(self):
        pytango_util = PyTango.Util.instance()
        for _device in pytango_util.get_device_list('*'):
            if (_device.get_name() ==
                    pytango_util.get_dserver_device().get_name()):
                continue
            for _id, _dev in _device.subscribe_event_id_dict.items():
                _dev.unsubscribe_event(_id)
        try:
            pytango_util.unregister_server()
        except PyTango.DevFailed as e:
            #Bypass any exception as no failure can be reported at
            #this stage
            pass
        self.delete_tango_device('/'.join(('dserver', self.device_family,
                                         self.server_name)))
        self.registry.stop()
        self.router.stop()

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
            #Use a new database connection in case the existing one was
            #shut down
            db = PyTango.Database()
            db.delete_device(device_name)
        except PyTango.DevFailed as e:
            pass
        except PyTango.ConnectionFailed as e:
            pass
