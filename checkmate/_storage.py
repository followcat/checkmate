import zope.interface

import checkmate._utils


def store_exchange(interface, name, description=None):
    """
        >>> import checkmate.test_data
        >>> import sample_app.exchanges
        >>> a = checkmate.test_data.App()
        >>> st = store_exchange(sample_app.exchanges.IAction, 'AP(R)')
        >>> ex = st.factory({'R': 'HIGH'})
        >>> (ex.action, ex.R) # doctest: +ELLIPSIS
        ('AP', <sample_app.data_structure.ActionRequest object at ...
    """
    code = checkmate._utils.internal_code(name)
    return checkmate._storage.ExchangeStorage(interface, name, description,
                getattr(checkmate._utils.get_module_defining(interface), code))

def store(interface, name, description=None):
    """
        >>> import checkmate.test_data
        >>> import sample_app.exchanges
        >>> a = checkmate.test_data.App()
        >>> st = store(sample_app.data_structure.IAttribute, "AT('AT1')")
        >>> attr = st.factory()
        >>> attr.value
        'AT1'
        >>> st = store(sample_app.data_structure.IAttribute, 'AT')
        >>> attr = st.factory()

        >>> st = store(sample_app.component_1.states.IAnotherState, 'Q0()')
        >>> state = st.factory()
        >>> state.value
        [None]
    """
    if checkmate._utils.method_unbound(name):
        code = checkmate._utils.internal_code(name)
        return checkmate._storage.InternalStorage(interface, name, description,
                getattr(checkmate._utils.get_class_implementing(interface), code))
    else:
        return checkmate._storage.InternalStorage(interface, name, description)


class PartitionStorage(object):
    def __init__(self, type, interface, codes, full_description=None):
        """ Build the list of InternalStorage
        """
        self.type = type
        self.storage = []
        for code in codes:
            try:
                code_description = full_description[code]
            except:
                code_description = (None,None,None)
            if ((type == 'states') or (type == 'data_structure')):
                _storage = store(interface, code, code_description)
                self.storage.append(_storage)
            elif type == 'exchanges':
                _storage = store_exchange(interface, code, code_description)
                self.storage.append(_storage)
        if codes == None or len(codes) == 0:
            self.storage.append(store(interface, ''))

    def get_description(self, item):
        """ Return description corresponding to item """
        for stored_item in list(self.storage):
            if item == stored_item.factory():
                return stored_item.description
        return (None,None,None)

class IStorage(zope.interface.Interface):
    """"""
    def factory(self, args=[], kwargs={}):
        """"""

@zope.interface.implementer(IStorage)
class InternalStorage(object):
    """Support local storage of data (status or data_structure) information in transition"""
    def __init__(self, interface, name ,description, function=None, arguments=None, kw_arguments=None):
        self.code = checkmate._utils.internal_code(name)
        self.description = description
        self.interface = interface
        self._class = checkmate._utils.get_class_implementing(interface)
        if function is None:
            self.function = self._class
        else:
            self.function = function
        if ((arguments is not None) and (kw_arguments is not None)):
            (self.arguments, self.kw_arguments) = (arguments, kw_arguments)
        else:
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

    def resolve(self, arg, states):
        """
            >>> import checkmate.test_data
            >>> import sample_app.component_1.states
            >>> a = checkmate.test_data.App()
            >>> st = InternalStorage(sample_app.component_1.states.IAnotherState, 'Q0(R)', None)
            >>> state = st.factory()
            >>> state.append(R=1)
            >>> st.resolve('R', [state])
            Traceback (most recent call last):
            ...
            AttributeError
            >>> st.resolve('Q0', [state])
            {'Q0': [{'R': 1}]}
        """
        if arg == self.code:
            for _state in states:
                if self.interface.providedBy(_state):
                    return {arg: _state.value}
        raise AttributeError

class ExchangeStorage(InternalStorage):
    """Support local storage of exchange information in transition"""

    def resolve(self, arg, exchange):
        """
            >>> import checkmate.test_data
            >>> import sample_app.exchanges
            >>> a = checkmate.test_data.App()
            >>> st = ExchangeStorage(sample_app.exchanges.IAction, 'AP(R)', None, sample_app.exchanges.AP)

            >>> ex = st.factory(kwargs={'R': 1})
            >>> st.resolve('R', ex)  # doctest: +ELLIPSIS
            {'R': 1}

            >>> ex = st.factory()
            >>> (ex.action, ex.parameters, ex.R) # doctest: +ELLIPSIS
            ('AP', {'R': None}, <sample_app.data_structure.ActionRequest object at ...
            >>> st.resolve('R', ex)  # doctest: +ELLIPSIS
            {'R': None}
        """
        if arg in list(self.kw_arguments.keys()):
            if arg in iter(exchange.parameters):
                return {arg: exchange.parameters[arg]}
        raise AttributeError

