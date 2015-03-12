# This code is part of the checkmate project.
# Copyright (C) 2013-2014 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import copy
import logging
import threading
import collections

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime._pyzmq
import checkmate.runtime.client
import checkmate.timeout_manager
import checkmate.runtime.launcher
import checkmate.runtime._threading


class ISut(zope.interface.Interface):
    """"""


class IStub(ISut):
    """"""
    def simulate(self, transition):
        """"""

    def validate(self, transition):
        """"""


class Component(object):
    def __init__(self, component):
        self.context = component
        self.client = checkmate.runtime.client.Client(self.context)
        self.logger = logging.getLogger('checkmate.runtime.component.Component')

    def setup(self, runtime):
        self.runtime = runtime

    def initialize(self):
        self.client.initialize()

    def start(self):
        self.context.start()
        self.client.start()

    def reset(self):
        self.context.reset()

    def stop(self):
        self.context.stop()
        self.client.stop()

    def process(self, exchanges):
        try:
            output = self.context.process(exchanges)
        except checkmate.component.NoTransitionFound:
            output = []
        self.logger.info("%s process exchange %s" % (self.context.name, exchanges[0].value))
        for _o in output:
            self.client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s send exchange %s to %s" % (self.context.name, _o.value, _o.destination))
        return output

    def simulate(self, transition):
        output = self.context.simulate(transition)
        for _o in output:
            self.client.send(_o)
            checkmate.logger.global_logger.log_exchange(_o)
            self.logger.info("%s simulate transition and output %s to %s" % (self.context.name, _o.value, _o.destination))
        return output

    def validate(self, transition):
        return self.context.validate(transition)


@zope.interface.implementer(ISut)
@zope.component.adapter(checkmate.component.IComponent)
class Sut(Component):
    """"""


@zope.interface.implementer(IStub)
@zope.component.adapter(checkmate.component.IComponent)
class Stub(Component):
    """"""


class ThreadedComponent(Component, checkmate.runtime._threading.Thread):
    """"""
    using_internal_client = False
    reading_internal_client = False
    using_external_client = True
    reading_external_client = True

    @checkmate.fix_issue('checkmate/issues/needless_socket.rst')
    def __init__(self, component):
        #Need to call both ancestors
        Component.__init__(self, component)
        checkmate.runtime._threading.Thread.__init__(self, name=component.name)

        self.exchange_deque = collections.deque()
        self.client = checkmate.runtime.client.ThreadedClient(self.context, self.exchange_deque)
        self.validation_lock = threading.Lock()

    def setup(self, runtime):
        super().setup(runtime)
        _application = runtime.application

        self.client.set_exchange_module(_application.exchange_module)

        if self.using_internal_client:
            connector_factory = checkmate.runtime._pyzmq.Connector
            _communication = runtime.communication_list['default']
            self.client.internal_connector = connector_factory(self.context, _communication, is_reading=self.reading_internal_client)
        if self.using_external_client:
            _communication = runtime.communication_list['']
            connector_factory = _communication.connector_class
            self.client.external_connector = connector_factory(self.context, _communication, is_reading=self.reading_external_client)

    def start(self):
        Component.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Component.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def run(self):
        def check_recv():
            return len(self.exchange_deque) > 0
        condition = threading.Condition()
        while True:
            if self.check_for_stop():
                break
            with condition:
                if condition.wait_for(check_recv, checkmate.timeout_manager.SAMPLE_APP_RECEIVE_SEC):
                    exchange = self.exchange_deque.popleft()
                    with self.validation_lock:
                        try:
                            self.process([exchange])
                        except Exception as e:
                            if not self.check_for_stop():
                                raise e

    def simulate(self, transition):
        return super().simulate(transition)

    @checkmate.timeout_manager.WaitOnFalse(checkmate.timeout_manager.VALIDATE_SEC, 100)
    def validate(self, transition):
        with self.validation_lock:
            return super().validate(transition)


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(ISut)
class ThreadedSut(ThreadedComponent, Sut):
    """"""
    using_internal_client = True
    reading_internal_client = True
    using_external_client = False
    reading_external_client = False

    def setup(self, runtime):
        super().setup(runtime)
        if hasattr(self.context, 'launch_command'):
            for communication_class in self.runtime.application.communication_list:
                communication_class(self.context)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(component=copy.deepcopy(self.context), runtime=self.runtime)

    def initialize(self):
        if hasattr(self.context, 'launch_command'):
            if hasattr(self.context, 'command_env'):
                self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command,
                                                                    command_env=self.context.command_env, component=self.context)
            else:
                self.launcher = checkmate.runtime.launcher.Launcher(command=self.context.launch_command, component=self.context)
        self.launcher.initialize()
        super(ThreadedSut, self).initialize()

    def start(self):
        self.launcher.start()
        super(ThreadedSut, self).start()

    def stop(self):
        self.launcher.end()
        super(ThreadedSut, self).stop()


@zope.component.adapter(checkmate.component.IComponent)
@zope.interface.implementer(IStub)
class ThreadedStub(ThreadedComponent, Stub):
    """"""
    using_internal_client = True
    reading_internal_client = False
    using_external_client = True
    reading_external_client = True

    def __init__(self, component):
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component)
