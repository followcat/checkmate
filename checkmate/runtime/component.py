# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import copy
import time
import queue
import logging
import threading
import multiprocessing

import zope.interface
import zope.component

import checkmate.logger
import checkmate.component
import checkmate.interfaces
import checkmate.runtime.client
import checkmate.timeout_manager
import checkmate.runtime.launcher
import checkmate.runtime._threading
import checkmate.runtime.interfaces


class Component(object):
    timeout_value = checkmate.timeout_manager.SAMPLE_APP_RECEIVE_SEC

    def __init__(self, component):
        self.context = component
        self.exchange_queue = multiprocessing.Queue()
        self.client = \
            checkmate.runtime.client.Client(self.context, self.exchange_queue)
        self.logger = \
            logging.getLogger('checkmate.runtime.component.Component')

    def setup(self, runtime):
        self.runtime = runtime

    def initialize(self):
        self.client.initialize()

    def start(self):
        output = self.context.start()
        self.client.start()
        if output is not None:
            for _o in output:
                self.client.send(_o)
                self.logger.info("Initializing: %s send exchange %s to %s" %
                    (self.context.name, _o.value, _o.destination))

    def reset(self):
        self.context.reset()

    def stop(self):
        self.context.stop()
        self.client.stop()

    def receive(self):
        return self.exchange_queue.get(timeout=self.timeout_value)

    def process(self, exchanges):
        """
            >>> import time
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.timeout_manager
            >>> import checkmate.runtime._runtime
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(\
                sample_app.application.TestData,\
                checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r.setup_environment(['C1', 'C2', 'C3'])
            >>> c1 = r.runtime_components['C1']
            >>> c2 = r.runtime_components['C2']
            >>> c3 = r.runtime_components['C3']
            >>> r.start_test()
            >>> pbac = sample_app.exchanges.ExchangeButton('PBAC')
            >>> outgoing = c2.process([pbac])
            >>> time.sleep(checkmate.timeout_manager.VALIDATE_SEC)
            >>> pbrl = sample_app.exchanges.ExchangeButton('PBRL')
            >>> outgoing = c2.process([pbrl])
            >>> time.sleep(checkmate.timeout_manager.VALIDATE_SEC)
            >>> pp = sample_app.exchanges.Action('PP')
            >>> outgoing = c1.process([pp])
            >>> time.sleep(checkmate.timeout_manager.VALIDATE_SEC)
            >>> items_c1 = ((pp,), tuple(c1.context.states))
            >>> items_c1 in c1.context.validation_dict.collected_items
            True
            >>> pa = [ _o for _o in outgoing if _o.value == 'PA'][0]
            >>> items_c2 = ((pa,), tuple(c2.context.states))
            >>> items_c2 in c2.context.validation_dict.collected_items
            True
            >>> items_c3 = ((pa,), tuple(c3.context.states))
            >>> items_c3 in c3.context.validation_dict.collected_items
            True
            >>> r.stop_test()
        """
        try:
            output = self.context.process(exchanges)
        except checkmate.exception.NoBlockFound:
            output = []
        self.logger.info("%s process exchange %s" %
            (self.context.name, exchanges[0].value))
        for _o in output:
            self.client.send(_o)
            self.logger.info("%s send exchange %s to %s" %
                (self.context.name, _o.value, _o.destination))
        return output

    def simulate(self, exchanges):
        for ex in exchanges:
            self.exchange_queue.put(ex)
            self.logger.info("%s simulate exchange %s to %s" %
                (self.context.name, ex.value, ex.destination))
        return exchanges

    def validate(self, block):
        return self.context.validate(block)


@zope.interface.implementer(checkmate.runtime.interfaces.ISut)
@zope.component.adapter(checkmate.interfaces.IComponent)
class Sut(Component):
    """"""


@zope.interface.implementer(checkmate.runtime.interfaces.IStub)
@zope.component.adapter(checkmate.interfaces.IComponent)
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
        checkmate.runtime._threading.Thread.__init__(self,
            name=component.name)

        self.client = checkmate.runtime.client.Client(self.context,
                        self.exchange_queue)
        self.validation_lock = threading.Lock()

    @checkmate.fix_issue('checkmate/issues/use_default_communication.rst')
    def setup(self, runtime):
        super().setup(runtime)
        if self.using_internal_client:
            _communication = runtime.communication_list['internal']
            self.client.internal_connector = \
                _communication.connector_factory(self.context,
                    queue=self.exchange_queue,
                    is_reading=self.reading_internal_client)
        if self.using_external_client:
            for _key in self.context.communication_list:
                _communication = runtime.communication_list[_key]
                self.client.external_connectors[_key] = \
                    _communication.connector_factory(self.context,
                        queue=self.exchange_queue,
                        is_reading=self.reading_external_client)

    def start(self):
        Component.start(self)
        checkmate.runtime._threading.Thread.start(self)

    def stop(self):
        Component.stop(self)
        checkmate.runtime._threading.Thread.stop(self)

    def run(self):
        while True:
            if self.check_for_stop():
                break
            try:
                exchange = self.receive()
                with self.validation_lock:
                    try:
                        self.process([exchange])
                    except Exception as e:
                        if not self.check_for_stop():
                            raise e
            except queue.Empty:
                pass

    @checkmate.timeout_manager.WaitOnFalse(
        checkmate.timeout_manager.VALIDATE_SEC, 100)
    def validate(self, block):
        with self.validation_lock:
            return super().validate(block)


@zope.component.adapter(checkmate.interfaces.IComponent)
@zope.interface.implementer(checkmate.runtime.interfaces.ISut)
class ThreadedSut(ThreadedComponent, Sut):
    """"""
    using_internal_client = True
    reading_internal_client = True
    using_external_client = False
    reading_external_client = False

    def __init__(self, component):
        super().__init__(component)
        if hasattr(self.context, 'launch_command'):
            self._launched_in_thread = False
        else:
            self._launched_in_thread = True

    def setup(self, runtime):
        self.communication_delay = runtime.communication_delay
        super().setup(runtime)
        if not self._launched_in_thread:
            for _name in self.context.communication_list:
                runtime.application.communication_list[_name](self.context)
        else:
            self.launcher = checkmate.runtime.launcher.Launcher(
                                command=ThreadedComponent,
                                component=copy.deepcopy(self.context),
                                threaded=self._launched_in_thread,
                                runtime=runtime)

    def initialize(self):
        if not self._launched_in_thread:
            if hasattr(self.context, 'command_env'):
                self.launcher = checkmate.runtime.launcher.Launcher(
                                    command=self.context.launch_command,
                                    command_env=self.context.command_env,
                                    threaded=self._launched_in_thread,
                                    component=self.context)
            else:
                self.launcher = checkmate.runtime.launcher.Launcher(
                                    command=self.context.launch_command,
                                    threaded=self._launched_in_thread,
                                    component=self.context)
        self.launcher.initialize()
        super(ThreadedSut, self).initialize()

    def simulate(self, exchanges):
        if self._launched_in_thread:
            self.launcher.simulate(exchanges)
            return super().simulate(exchanges)
        raise ValueError("Launcher SUT can't simulate")

    def validate(self, block):
        time.sleep(self.communication_delay)
        return super().validate(block)

    def start(self):
        self.launcher.start()
        super(ThreadedSut, self).start()

    def stop(self):
        self.launcher.end()
        super(ThreadedSut, self).stop()


@zope.component.adapter(checkmate.interfaces.IComponent)
@zope.interface.implementer(checkmate.runtime.interfaces.IStub)
class ThreadedStub(ThreadedComponent, Stub):
    """"""
    using_internal_client = True
    reading_internal_client = True
    using_external_client = True
    reading_external_client = True

    def __init__(self, component):
        #Call ThreadedStub first ancestor: ThreadedComponent expected
        super(ThreadedStub, self).__init__(component)
        self.received_internal_exchanges = []

    def setup(self, runtime):
        self.internal_queue = multiprocessing.Queue()
        super(ThreadedStub, self).setup(runtime)
        self.client.internal_connector.queue = self.internal_queue

    def receive(self):
        exchange = self.exchange_queue.get(timeout=self.timeout_value)        
        while True:
            if exchange in self.received_internal_exchanges:
                self.received_internal_exchanges.remove(exchange)
                return exchange
            try:
                self.received_internal_exchanges.append(
                    self.internal_queue.get(timeout=self.timeout_value))
            except queue.Empty:
                pass

    def reset(self):
        self.received_internal_exchanges = []
        super(ThreadedStub, self).reset()

    def simulate(self, exchanges):
        for ex in exchanges:
            self.internal_queue.put(ex)
        return super().simulate(exchanges)

