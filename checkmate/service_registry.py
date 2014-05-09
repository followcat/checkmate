import copy

import zope.interface
import zope.interface.interface
import zope.component.interfaces
import zope.component.globalregistry

import checkmate.exchange


@zope.component.adapter(checkmate.exchange.IExchange)
@zope.interface.implementer(zope.component.interfaces.IFactory)
class ServiceFactory(object):
    """"""
    def __init__(self, exchange):
        """"""
        self.context = exchange

    def __call__(self, origin, destinations):
        """"""
        for _d in destinations:
            exchange = copy.deepcopy(self.context)
            exchange.origin_destination(origin, _d)
            yield exchange
        yield from ()


class ServiceRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """
    """
    def __init__(self):
        super(ServiceRegistry, self).__init__()
        self.registerAdapter(ServiceFactory, (checkmate.exchange.IExchange,), zope.component.interfaces.IFactory)
        self._registry = {}

    def register(self, component, services):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> _service = c1.state_machine.transitions[0].incoming[0].interface
            >>> c1.service_registry._registry[_service]
            ['C1']
        """
        for _service in services:
            assert isinstance(_service, zope.interface.interface.InterfaceClass)
            if _service in self._registry.keys():
                if component.name not in self._registry[_service]:
                    self._registry[_service].append(component.name)
            else:
                self._registry[_service] = [component.name]

    def server_exchanges(self, exchange, component_name=''):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> c3 = a.components['C3']
            >>> e = c1.state_machine.transitions[0].outgoing[0].factory()
            >>> for _e in c1.service_registry.server_exchanges(e, 'C1'):
            ...     print(_e.destination)
            C3
        """
        _factory = self.getAdapter(exchange, zope.component.interfaces.IFactory)
        for _service, _servers in self._registry.items():
            if _service.providedBy(exchange):
                return _factory(component_name, _servers)
        return _factory(component_name, [])
