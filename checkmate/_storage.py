import checkmate._utils


def store_data_structure(interface, name, description=None):
    """
        >>> import checkmate.test_data
        >>> import sample_app.exchanges
        >>> a = checkmate.test_data.App()
        >>> store = store_data_structure(sample_app.data_structure.IAttribute, "AT('AT1')")
        >>> attr = store.factory()
        >>> attr.state
        'AT1'
        >>> store = store_data_structure(sample_app.data_structure.IAttribute, 'AT')
        >>> attr = store.factory()
    """
    return checkmate._storage.DataStructureStorage(interface, name, description)

def store_exchange(interface, name, description=None):
    """
        >>> import checkmate.test_data
        >>> import sample_app.exchanges
        >>> a = checkmate.test_data.App()
        >>> store_ex = store_exchange(sample_app.exchanges.IAction, 'AP(R)')
        >>> ex = store_ex.factory({'R': 'HIGH'})
        >>> (ex.action, ex.R) # doctest: +ELLIPSIS
        ('AP', <checkmate._storage.DataStructureStorage object at ...
    """
    code = checkmate._utils.internal_code(name)
    return checkmate._storage.ExchangeStorage(interface, name, description,
                getattr(checkmate._utils.get_module_defining(interface), code))

def store_state(interface, name, description=None):
    """
        >>> import checkmate.test_data
        >>> import sample_app.component_1.states
        >>> a = checkmate.test_data.App()
        >>> store_st = store_state(sample_app.component_1.states.IAnotherState, 'Q0()')
        >>> state = store_st.factory()
        >>> state.value
        [None]
    """
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
        if codes == None or len(codes) == 0:
            self.storage.append(store_data_structure(interface, ''))

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
        """
            >>> 'Q0.append(R)'
            'Q0.append(R)'
            >>> 'R(P=HIGH)'
            'R(P=HIGH)'
        """
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
        """
            >>> import checkmate.test_data
            >>> import sample_app.component_1.states
            >>> a = checkmate.test_data.App()
            >>> store_st = StateStorage(sample_app.component_1.states.IAnotherState, 'Q0(R)', None)
            >>> state = store_st.factory()
            >>> state.append(R=1)
            >>> store_st.resolve('R', [state])
            Traceback (most recent call last):
            ...
            AttributeError
            >>> store_st.resolve('Q0', [state])
            [{'R': 1}]
        """
        if arg == self.code:
            for _state in states:
                if self.interface.providedBy(_state):
                    return _state.value
        raise AttributeError

class ExchangeStorage(InternalStorage):
    """Support local storage of exchange information in transition"""

    def resolve(self, arg, exchange):
        """
            >>> import checkmate.test_data
            >>> import sample_app.exchanges
            >>> a = checkmate.test_data.App()
            >>> store_ex = ExchangeStorage(sample_app.exchanges.IAction, 'AP(R)', None, sample_app.exchanges.AP)
            >>> ex = store_ex.factory()
            >>> (ex.action, ex.parameters, ex.R) # doctest: +ELLIPSIS
            ('AP', {'R': None}, <checkmate._storage.DataStructureStorage object at ...
            >>> store_ex.resolve('R', ex)
        """
        if arg in list(self.kw_arguments.keys()):
            if arg in iter(exchange.parameters):
                return exchange.parameters[arg]
        raise AttributeError

