import checkmate._utils


def store_data_structure(interface, name, description=None):
    return checkmate._storage.DataStructureStorage(interface, name, description)

def store_exchange(interface, name, description=None):
    code = checkmate._utils.internal_code(name)
    return checkmate._storage.ExchangeStorage(interface, name, description,
                getattr(checkmate._utils.get_module_defining(interface), code))

def store_state(interface, name, description=None):
    if checkmate._utils.method_unbound(name):
        code = checkmate._utils.internal_code(name)
        return checkmate._storage.StateStorage(interface, name, description,
                getattr(checkmate._utils.get_class_implementing(interface), code))
    else:
        return checkmate._storage.StateStorage(interface, name, description)

def store_state_value(interface, name, description=None):
    (arguments, kw_arguments) = checkmate._utils.method_value_arguments(name)
    return checkmate._storage.StateStorage(interface, name, description, arguments=arguments, kw_arguments=kw_arguments)

class PartitionStorage(object):
    def __init__(self, type, interface, codes, full_description):
        """ Build the list of InternalStorage
        """
        self.type = type
        self.storage = []
        for code in codes:
            if type == 'states':
                _storage = store_state_value(interface, code, full_description[code])
                self.storage.append(_storage)
            elif type == 'data_structure':
                _storage = store_data_structure(interface, code, full_description[code])
                self.storage.append(_storage)
            elif type == 'exchanges':
                _storage = store_exchange(interface, code, full_description[code])
                self.storage.append(_storage)

    def get_description(self, item):
        """ Return description corresponding to item """
        for stored_item in list(self.storage):
            if item == stored_item.factory():
                return stored_item.description
        return (None,None,None)

class InternalStorage(object):
    def __init__(self, interface, name, description, function=None):
        self.code = checkmate._utils.internal_code(name)
        self.description = description
        self.interface = interface
        self._class = checkmate._utils.get_class_implementing(interface)
        if function is None:
            self.function = self._class
        else:
            self.function = function
        (self.arguments, self.kw_arguments) = checkmate._utils.method_arguments(name)

    def factory(self, args=[], kwargs={}):
        def wrapper(func, param, kwparam):
            return func(*param, **kwparam)

        if len(args) == 0:
            args = self.arguments
        if len(kwargs) == 0:
            kwargs = self.kw_arguments
        return wrapper(self.function, args, kwargs)

class DataStructureStorage(InternalStorage):
    """Support local storage of data structure information in transition"""

class StateStorage(InternalStorage):
    """Support local storage of state information in transition"""
    def __init__(self, interface, name ,description, function=None, arguments=None, kw_arguments=None):
        super(StateStorage, self).__init__(interface, name, description, function)
        if ((arguments is not None) and (kw_arguments is not None)):
            (self.arguments, self.kw_arguments) = (arguments, kw_arguments)

    def resolve(self, arg, states):
        if arg == self.code:
            for _state in states:
                if self.interface.providedBy(_state):
                    return _state.value
        raise AttributeError

class ExchangeStorage(InternalStorage):
    """Support local storage of exchange information in transition"""

    def resolve(self, arg, exchange):
        if arg in list(self.kw_arguments.keys()):
            if arg in iter(exchange.parameters):
                return exchange.parameters[arg]
        raise AttributeError

