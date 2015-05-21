# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.component.globalregistry


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
            >>> _t = c1.engine.blocks[0]
            >>> _class = _t.incoming[0].partition_class
            >>> c1.service_registry._registry[_class]
            ['C1']
        """
        for _class in classes:
            if _class not in self._registry.keys():
                self._registry[_class] = []
            if component.name not in self._registry[_class]:
                self._registry[_class].append(component.name)
                
    def server_exchanges(self, exchange, component_name=''):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> c1 = a.components['C1']
            >>> c3 = a.components['C3']
            >>> _t = c1.engine.blocks[0]
            >>> e = _t.outgoing[0].factory()
            >>> for _e in c1.service_registry.server_exchanges(e, 'C1'):
            ...     print(_e.destination)
            ['C3']
        """
        destinations = []
        for _class, _servers in self._registry.items():
            if isinstance(exchange, _class):
                destinations = _servers
                break
        if exchange.broadcast:
            destinations = [destinations]
        for _d in destinations:
            new_exchange = exchange.partition_storage.partition_class(exchange)
            new_exchange.carbon_copy(exchange)
            new_exchange.origin_destination(component_name, _d)
            yield new_exchange
