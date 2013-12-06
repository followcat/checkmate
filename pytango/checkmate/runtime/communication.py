import sys
import shlex

import PyTango

import checkmate.runtime.communication
import checkmate.runtime._threading


class Registry(checkmate.runtime._threading.Thread):
    def __init__(self):
        super(Registry, self).__init__()
        self.pytango_util = PyTango.Util.instance()

    def check_for_shutdown(self):
        if self.check_for_stop():
            sys.exit(0)
    
    def run(self):
        self.pytango_util.server_init()
        self.pytango_util.server_set_event_loop(self.check_for_shutdown)
        self.pytango_util.server_run()


class Connector(checkmate.runtime.communication.Connector):
    """"""


class Communication(checkmate.runtime.communication.Communication):
    def __init__(self):
        super(Communication, self).__init__()
        self.pytango_server = PyTango.Util(shlex.split(__file__ + ' C1'))
        self.connector = Connector

    def initialize(self):
        """"""
        super(Communication, self).initialize()
        self.registry = Registry()
        self.registry.start()

    def close(self):
        pytango_util = PyTango.Util.instance()
        pytango_util.unregister_server()
        self.registry.stop()

