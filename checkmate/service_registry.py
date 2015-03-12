import copy

import zope.interface
import zope.interface.interface
import zope.component.interfaces
import zope.component.globalregistry

import checkmate.interfaces


@zope.component.adapter(checkmate.interfaces.IExchange)
@zope.interface.implementer(zope.component.interfaces.IFactory)
class ServiceFactory(object):
    """"""
    def __init__(self, exchange):
        """"""
        self.context = exchange

    def __call__(self, origin, destinations):
        """"""
        if self.context.broadcast:
            exchange = copy.deepcopy(self.context)
            exchange.origin_destination(origin, destinations)
            yield exchange
        else:
            for _d in destinations:
                exchange = copy.deepcopy(self.context)
                exchange.origin_destination(origin, _d)
                yield exchange
        yield from ()


class ServiceRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """"""
    def __init__(self):
        super(ServiceRegistry, self).__init__()
        self._registry = {}

    def register(self, component, classes):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> _t = c1.state_machine.transitions[0]
            >>> _class = _t.incoming[0].partition_class
            >>> c1.service_registry._registry[_class]
            ['C1']
        """
        for _class in classes:
            if _class in self._registry.keys():
                if component.name not in self._registry[_class]:
                    self._registry[_class].append(component.name)
            else:
                self._registry[_class] = [component.name]

    def server_exchanges(self, exchange, component_name=''):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> c3 = a.components['C3']
            >>> _t = c1.state_machine.transitions[0]
            >>> e = _t.outgoing[0].factory()
            >>> for _e in c1.service_registry.server_exchanges(e, 'C1'):
            ...     print(_e.destination)
            ['C3']
        """
        for _class, _servers in self._registry.items():
            if isinstance(exchange, _class):
                return self._factory(exchange, component_name, _servers)
        return self._factory(exchange, component_name, [])

    def _factory(self, exchange, origin, destinations):
        """"""
        if exchange.broadcast:
            new_exchange = copy.deepcopy(exchange)
            new_exchange.origin_destination(origin, destinations)
            yield new_exchange
        else:
            for _d in destinations:
                new_exchange = copy.deepcopy(exchange)
                new_exchange.origin_destination(origin, _d)
                yield new_exchange
        yield from ()
