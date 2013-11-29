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
    def __init__(self, application, communication, threaded=False):
        """"""
        self.threaded = threaded
        self.application = application()
        self.communication_list = [(communication(), 'default')]
        for _communication in self.application.communication_list:
            self.communication_list.append((_communication(), ''))
        for (_name, _component) in self.application.components.items():
            if hasattr(_component, 'communication_list'):
                for _communication in _component.communication_list:
                    self.communication_list.append((_communication(), _name))

        if self.threaded:
            checkmate.runtime.registry.global_registry.registerUtility(self, checkmate.runtime.interfaces.IRuntime)
        checkmate.runtime.registry.global_registry.registerUtility(self.application, checkmate.application.IApplication)
        if threaded:
            checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.ThreadedStub,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.ThreadedSut,
                                                                       (checkmate.component.IComponent,), checkmate.runtime.component.ISut)
        else:
            checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.Stub, (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
            checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.Sut, (checkmate.component.IComponent,), checkmate.runtime.component.ISut)

    def setup_environment(self, sut):
        checkmate.logger.global_logger.start_exchange_logger()
        self.application.sut(sut)
        self.application.build_test_plan()

        for (communication, type) in self.communication_list:
            communication.initialize()
            checkmate.runtime.registry.global_registry.registerUtility(zope.component.factory.Factory(communication.connector), zope.component.interfaces.IFactory, type)

        for component in self.application.stubs:
            stub = checkmate.runtime.registry.global_registry.getAdapter(self.application.components[component], checkmate.runtime.component.IStub)
            checkmate.runtime.registry.global_registry.registerUtility(stub, checkmate.component.IComponent, component)

        for component in self.application.system_under_test:
            sut = checkmate.runtime.registry.global_registry.getAdapter(self.application.components[component], checkmate.runtime.component.ISut)
            checkmate.runtime.registry.global_registry.registerUtility(sut, checkmate.component.IComponent, component)


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
        # Start stubs first
        component_list = self.application.stubs + self.application.system_under_test
        for name in component_list:
            _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
            _component.start()


    def still_busy(self):
        if self.threaded == False:
            return False
        component_list = self.application.system_under_test + self.application.stubs
        for name in component_list:
            _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
            if _component.is_busy():
                return True
        return False

    def wait_till_not_busy(self):
        while self.still_busy():
            pass

    def stop_test(self):
        # Stop stubs last
        component_list = self.application.system_under_test + self.application.stubs
        # Wait untill all the components are not busy
        self.wait_till_not_busy()
        for name in component_list:
            _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
            _component.stop()
            #if self.threaded:
            #    _component.join()
        for (communication, type) in self.communication_list:
            communication.close()
        checkmate.logger.global_logger.stop_exchange_logger()

