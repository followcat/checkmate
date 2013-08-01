import checkmate._utils


def store_data_structure(interface, name):
    _arguments, _kw_arguments = checkmate._utils.method_arguments(name)
    return checkmate._storage.DataStructureStorage(checkmate._utils.internal_code(name), interface,
                getattr(checkmate._utils.get_module_defining(interface), checkmate._utils.internal_code(name)),
                _arguments, kw_arguments=_kw_arguments)

def store_exchange(interface, name):
    _arguments, _kw_arguments = checkmate._utils.method_arguments(name)
    return checkmate._storage.ExchangeStorage(checkmate._utils.internal_code(name), interface,
                getattr(checkmate._utils.get_module_defining(interface), checkmate._utils.internal_code(name)),
                _arguments, kw_arguments=_kw_arguments)

def store_state(interface, name):
    _o = checkmate._utils.get_class_implementing(interface)
    _arguments, _kw_arguments = checkmate._utils.method_arguments(name)
    if checkmate._utils.method_unbound(name):
        return checkmate._storage.StateStorage(checkmate._utils.internal_code(name), interface,
                                getattr(_o, checkmate._utils.internal_code(name)), _arguments, kw_arguments=_kw_arguments)
    else:
        return checkmate._storage.StateStorage(checkmate._utils.internal_code(name), interface,
                    _o, _arguments, kw_arguments=_kw_arguments)

def store_state_value(interface, name):
    _o = checkmate._utils.get_class_implementing(interface)
    _arguments, _kw_arguments = checkmate._utils.method_value_arguments(name)
    return checkmate._storage.StateStorage(checkmate._utils.internal_code(name), interface,
                    _o, _arguments, kw_arguments=_kw_arguments)

class InternalStorage(object):
    def __init__(self, code, interface, function, arguments, kw_arguments={}):
        self.code = code
        self.function = function
        self.arguments = arguments
        self.kw_arguments = kw_arguments
        self.interface = interface

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

