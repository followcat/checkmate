import os
import copy
import time
import pickle
import os.path

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

    def __call__(self, origin, destinations, wf, log=False):
        """"""
        for _d in destinations:
            exchange = copy.deepcopy(self.context)
            exchange.origin_destination(origin, _d)
            if log:
                pickle.dump(exchange, wf)
            yield exchange
        yield from ()


class ServiceRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """
    """
    def __init__(self):
        super(ServiceRegistry, self).__init__()
        self.registerAdapter(ServiceFactory, (checkmate.exchange.IExchange,), zope.component.interfaces.IFactory)
        self._registry = {}
        filename = os.path.join(os.getenv("CHECKMATE_LOG", "."), "exchange-" + time.asctime().replace(' ', '-') + ".log")
        self.wf = open(filename, 'wb')

    def __del__(self):
        self.wf.flush()
        self.wf.close()

    def register(self, component, services):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> r = checkmate.service_registry.global_registry
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> _service = c1.state_machine.transitions[0].incoming[0].interface
            >>> r.register(c1, (_service,))
            >>> r._registry[_service]
            ['C1']
        """
        for _service in services:
            assert isinstance(_service, zope.interface.interface.InterfaceClass)
            if _service in self._registry.keys():
                if component.name not in self._registry[_service]:
                    self._registry[_service].append(component.name)
            else:
                self._registry[_service] = [component.name]

    def server_exchanges(self, exchange, component, log=False):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> r = checkmate.service_registry.global_registry
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> c3 = a.components['C3']
            >>> _service = c1.state_machine.transitions[0].outgoing[0].interface
            >>> r.register(c3, (_service,))
            >>> e = c1.state_machine.transitions[0].outgoing[0].factory()
            >>> for _e in r.server_exchanges(e, c1):
            ...     print(_e.destination)
            C3
        """
        _factory = self.getAdapter(exchange, zope.component.interfaces.IFactory)
        for _service, _servers in self._registry.items():
            if _service.providedBy(exchange):
                return _factory(component.name, _servers, self.wf, log)
        return _factory(component.name, [], self.wf, log)

global_registry = ServiceRegistry()

