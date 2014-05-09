import sys
import logging
import threading

import zope.interface
import zope.component
import zope.component.interfaces

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.interfaces


TIMEOUT_THREAD_STOP = 1


@zope.interface.implementer(checkmate.runtime.interfaces.IRuntime)
@zope.component.adapter((checkmate.application.IApplication, checkmate.runtime.interfaces.IProtocol))
class Runtime(object):
    """"""
    def __init__(self, application, communication, threaded=False):
        """"""
        self.threaded = threaded
        self.runtime_components = {}
        self.communication_list = {}
        self.application_class = application
        self.application = application()
        self._registry = checkmate.runtime.registry.RuntimeGlobalRegistry()

        self.communication_list['default'] = communication()

        for _c in self.application.communication_list:
            _communication = _c()
            self.communication_list[''] = _communication

        if self.threaded:
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedStub,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.ThreadedSut,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.ISut)
        else:
            self._registry.registerAdapter(checkmate.runtime.component.Stub,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            self._registry.registerAdapter(checkmate.runtime.component.Sut,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.ISut)

    def setup_environment(self, sut):
        checkmate.logger.global_logger.start_exchange_logger()
        logging.getLogger('checkmate.runtime._runtime.Runtime').info("%s"%(sys.argv))
        self.application.sut(sut)

        for component in self.application.stubs:
            stub = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.IStub)
            self.runtime_components[component] = stub
            stub.setup(self)

        for component in self.application.system_under_test:
            sut = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.ISut)
            self.runtime_components[component] = sut
            sut.setup(self)

        for communication in self.communication_list.values():
            communication.initialize()

        for name in self.application.stubs + self.application.system_under_test:
            _component = self.runtime_components[name]
            _component.initialize()

    def start_test(self):
        """
            >>> import checkmate.runtime
            >>> import checkmate.component
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> ac = sample_app.application.TestData
            >>> cc = checkmate.runtime.communication.Communication
            >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> c2_stub = r.runtime_components['C2']
            >>> checkmate.runtime.component.IStub.providedBy(c2_stub)
            True
            >>> a = r.application
            >>> simulated_transition = a.components['C2'].state_machine.transitions[0]
            >>> o = c2_stub.simulate(simulated_transition) # doctest: +ELLIPSIS
            >>> c1 = r.runtime_components['C1']
            >>> checkmate.runtime.component.IStub.providedBy(c1)
            False
            >>> c1.process(o) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> r.stop_test()
        """
        for communication in self.communication_list.values():
            communication.start()
        # Start stubs first
        component_list = self.application.stubs + self.application.system_under_test
        for name in component_list:
            _component = self.runtime_components[name]
            _component.start()

    def stop_test(self):
        # Stop stubs last
        for name in self.application.system_under_test + self.application.stubs:
            _component = self.runtime_components[name]
            _component.stop()
            #if self.threaded:
            #    _component.join()
        for communication in self.communication_list.values():
            communication.close()

        def check_threads():
            return len(threading.enumerate()) == 1
        condition = threading.Condition()
        with condition:
            condition.wait_for(check_threads, TIMEOUT_THREAD_STOP)

        checkmate.logger.global_logger.stop_exchange_logger()

