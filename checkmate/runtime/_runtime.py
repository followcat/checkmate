import sys
import logging

import zope.interface
import zope.component
import zope.component.interfaces

import checkmate.logger
import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IRuntime)
@zope.component.adapter((checkmate.application.IApplication, checkmate.runtime.interfaces.IProtocol))
class Runtime(object):
    """"""
    def __init__(self, application, communication, threaded=False, full_python=True):
        """"""
        self.threaded = threaded
        self.application_class = application
        self.application = application(full_python=full_python)
        self._registry = checkmate.runtime.registry.RuntimeGlobalRegistry()
        checkmate.runtime.registry.global_registry = self._registry
        self._registry.registerUtility(self.application, checkmate.application.IApplication)

        self.communication_list = [(communication(), 'default')]

        for _c in self.application.communication_list:
            _communication = _c()
            self.communication_list.append((_communication, ''))

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

        self.reg_key = (''.join(sut), self.application_class)
        checkmate.runtime.registry.global_registries_dict[self.reg_key] = self._registry
        for (communication, type) in self.communication_list:
            self._registry.registerUtility(communication, checkmate.runtime.interfaces.ICommunication, type)

        for component in self.application.stubs:
            setattr(self.application.components[component], 'reg_key', self.reg_key)
            stub = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.IStub)
            self._registry.registerUtility(stub, checkmate.component.IComponent, component)

        for component in self.application.system_under_test:
            setattr(self.application.components[component], 'reg_key', self.reg_key)
            sut = self._registry.getAdapter(self.application.components[component], checkmate.runtime.component.ISut)
            self._registry.registerUtility(sut, checkmate.component.IComponent, component)

        import time; time.sleep(1)
        for (communication, type) in self.communication_list:
            communication.initialize()

        for name in self.application.stubs + self.application.system_under_test:
            _component = self._registry.getUtility(checkmate.component.IComponent, name)
            _component.initialize()

    def start_test(self):
        """
            >>> import checkmate.test_data
            >>> import checkmate.runtime
            >>> import checkmate.component
            >>> import checkmate.runtime.communication
            >>> del checkmate.test_data.my_data
            >>> checkmate.test_data.my_data = {}
            >>> ac = checkmate.test_data.App
            >>> cc = checkmate.runtime.communication.Communication
            >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> c2_stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
            >>> checkmate.runtime.component.IStub.providedBy(c2_stub)
            True
            >>> a = r.application
            >>> simulated_exchange = a.components['C2'].state_machine.transitions[0].outgoing[0].factory()
            >>> o = c2_stub.simulate(simulated_exchange) # doctest: +ELLIPSIS
            >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
            >>> checkmate.runtime.component.IStub.providedBy(c1)
            False
            >>> c1.process(o) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> r.stop_test()
        """
        for (communication, type) in self.communication_list:
            communication.start()
        # Start stubs first
        component_list = self.application.stubs + self.application.system_under_test
        for name in component_list:
            _component = self._registry.getUtility(checkmate.component.IComponent, name)
            _component.start()

    def stop_test(self):
        # Stop stubs last
        for name in self.application.system_under_test + self.application.stubs:
            _component = self._registry.getUtility(checkmate.component.IComponent, name)
            _component.stop()
            #if self.threaded:
            #    _component.join()
        for (communication, type) in self.communication_list:
            communication.close()
        checkmate.logger.global_logger.stop_exchange_logger()

