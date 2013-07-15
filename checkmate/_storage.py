import checkmate._utils


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

class StateStorage(InternalStorage):
    """Support local storage of state information in transition"""

class ExchangeStorage(InternalStorage):
    """Support local storage of exchange information in transition"""

