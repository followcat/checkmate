import zope.interface
import zope.component

import checkmate.component
import checkmate.application
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.communication


class IRuntime(zope.interface.Interface):
    """"""

@zope.interface.implementer(IRuntime)
@zope.component.adapter((checkmate.application.IApplication, checkmate.runtime.communication.IProtocol))
class Runtime(object):
    """"""
    def __init__(self, application, communication):
        """"""
        self.application = application
        self.communication = communication

        checkmate.runtime.registry.global_registry.registerUtility(self.communication.connection_handler, checkmate.runtime.communication.IConnection)
        checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.Stub, (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
        checkmate.runtime.registry.global_registry.registerAdapter(checkmate.runtime.component.Sut, (checkmate.component.IComponent,), checkmate.runtime.component.ISut)

    def setup_environment(self, sut):
        self.application.sut(sut)
        self.application.build_test_plan()

        self.communication.initialize()
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
            >>> a = checkmate.test_data.App()
            >>> c = checkmate.runtime.communication.Communication()
            >>> r = checkmate.runtime._runtime.Runtime(a, c)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> c2_stub = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
            >>> checkmate.runtime.component.IStub.providedBy(c2_stub)
            True
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


    def stop_test(self):
        # Stop stubs last
        component_list = self.application.system_under_test + self.application.stubs
        for name in component_list:
            _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, name)
            _component.stop()
        self.communication.close()

