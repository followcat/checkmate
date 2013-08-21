import copy
import collections

import zope.interface

import checkmate._utils


def _build_resolve_logic(transition, type, data):
    """
        >>> import checkmate.test_data
        >>> import sample_app.exchanges
        >>> a = checkmate.test_data.App()
        >>> t = a.components['C1'].state_machine.transitions[1]
        >>> _build_resolve_logic(t, 'final', t.final[0])
        {'R': ('incoming', <InterfaceClass sample_app.exchanges.IAction>)}
    """
    resolved_arguments = {}
    entry = getattr(transition, type)
    if type == 'incoming':
        arguments = list(entry.arguments.attribute_values.keys())
    else:
        arguments = list(entry[entry.index(data)].arguments.attribute_values.keys())
    for arg in arguments:
        found = False
        if type in ['final', 'incoming']:
            for item in transition.initial:
                if arg == item.code:
                    resolved_arguments[arg] = ('initial', item.interface)
                    found = True
                    break
        if ((not found) and transition.incoming is not None):
            if type in ['final', 'outgoing']:
                if arg in list(transition.incoming.arguments.attribute_values.keys()):
                    resolved_arguments[arg] = ('incoming', transition.incoming.interface)
                    found = True
        if not found:
            if type in ['outgoing']:
                for item in transition.final:
                    if arg == item.code:
                        resolved_arguments[arg] = ('final', item.interface)
                        found = True
                        break
    return resolved_arguments


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
    try:
        return checkmate._storage.ExchangeStorage(interface, name, description,
                getattr(checkmate._utils.get_module_defining(interface), code))
    except AttributeError:
        raise AttributeError(checkmate._utils.get_module_defining(interface).__name__+" has no function defined: "+code)

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
        try:
            return checkmate._storage.InternalStorage(interface, name, description,
                    getattr(checkmate._utils.get_class_implementing(interface), code))
        except AttributeError:
            raise AttributeError(checkmate._utils.get_class_implementing(interface).__name__+' has no function defined: '+code)
    else:
        return checkmate._storage.InternalStorage(interface, name, description)

class Data(object):
    def __init__(self, type, interface, codes, full_description=None):
        self.type = type
        self.interface = interface
        self.codes = codes
        self.full_description = full_description

    def storage(self):
        _list = []
        for code in self.codes:
            try:
                code_description = self.full_description[code]
            except:
                code_description = (None,None,None)
            if ((self.type == 'states') or (self.type == 'data_structure')):
                _storage = store(self.interface, code, code_description)
                _list.append(_storage)
            elif self.type == 'exchanges':
                _storage = store_exchange(self.interface, code, code_description)
                _list.append(_storage)
        if self.codes == None or len(self.codes) == 0:
            _list.append(store(self.interface, ''))
        return _list
        

class TransitionData(collections.OrderedDict):
    def __init__(self, initial, incoming, final, outgoing):
        assert type(final) == list
        assert type(initial) == list
        assert type(outgoing) == list

        assert (incoming is None or isinstance(incoming, Data))
        for item in initial + final + outgoing:
            assert isinstance(item, Data)

        super(TransitionData, self).__init__()
        # OrderedDict to keep order ('initial', 'incoming', 'final', 'outgoing')
        self['initial'] = initial
        self['incoming'] = incoming
        self['final'] = final
        self['outgoing'] = outgoing
    
class StorageManager(object):
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

class PartitionStorage(object):
    def __init__(self, data):
        """ Build the list of InternalStorage
        """
        assert isinstance(data, Data)
        self.type = data.type
        self.storage = data.storage()

    def get_description(self, item):
        """ Return description corresponding to item """
        for stored_item in list(self.storage):
            if item == stored_item.factory():
                return stored_item.description
        return (None,None,None)


class TransitionStorage(object):
    def __init__(self, transition):
        """ Build the list of InternalStorage
        """
        assert isinstance(transition, TransitionData)
        for key in iter(transition):
            if key == 'incoming':
                try:
                    self.incoming = transition[key].storage()[0]
                except:
                    self.incoming = None
            else:
                _list = []
                for item in transition[key]:
                    _list.append(item.storage()[0])
                setattr(self, key, _list)

        if self.incoming is not None:
            self.resolve_logic = _build_resolve_logic(self, 'incoming', self.incoming)
        for final_state in self.final:
            final_state.resolve_logic = _build_resolve_logic(self, 'final', final_state)
        for outgoing_exchange in self.outgoing:
            outgoing_exchange.resolve_logic = _build_resolve_logic(self, 'outgoing', outgoing_exchange)


class IStorage(zope.interface.Interface):
    """"""
    def factory(self, args=[], kwargs={}):
        """"""

@zope.interface.implementer(IStorage)
class InternalStorage(object):
    """Support local storage of data (status or data_structure) information in transition"""
    def __init__(self, interface, name ,description, function=None):
        """
            >>> import checkmate.test_data
            >>> import sample_app.data_structure
            >>> a = checkmate.test_data.App()
            >>> st = InternalStorage(sample_app.data_structure.IActionPriority, 'P(HIGH)', None, sample_app.data_structure.ActionPriority)
            >>> st.factory().value
            'HIGH'
            >>> st = InternalStorage(sample_app.data_structure.IActionPriority, 'HIGH', None, sample_app.data_structure.ActionPriority)
            >>> st.factory().value # doctest: +SKIP
            'HIGH'
        """
        self.code = checkmate._utils.internal_code(name)
        self.description = description
        self.interface = interface
        self._class = checkmate._utils.get_class_implementing(interface)
        if function is None:
            self.function = self._class
        else:
            self.function = function

        self.arguments = checkmate._utils.method_arguments(name)
        self.resolve_logic = {}

    def factory(self, args=[], kwargs={}):
        """
            >>> 'Q0.append(R)'
            'Q0.append(R)'

            >>> import checkmate.test_data
            >>> import sample_app.data_structure
            >>> a = checkmate.test_data.App()
            >>> st = InternalStorage(sample_app.data_structure.IActionRequest, 'R', None, sample_app.data_structure.ActionRequest)
            >>> r1 = st.factory(kwargs={'P': 'HIGH'})
            >>> r1.P.value
            'HIGH'
            >>> st = InternalStorage(sample_app.data_structure.IActionRequest, 'R(P=HIGH,A=AT2)', None, sample_app.data_structure.ActionRequest)
            >>> r = st.factory()
            >>> (r.P.value, r.A.value)
            ('HIGH', 'AT2')
            >>> r = st.factory(kwargs={'P': 'NORM'})
            >>> (r.P.value, r.A.value)
            ('NORM', 'AT2')
        """
        def wrapper(func, param, kwparam):
            if type(args) == list and self.interface.implementedBy(self.function):
                if len(self.arguments.values) > 0 and len(args) > 0:
                    func = self.function.__init__
                    state = args[0]
                    value = self.arguments.values[0]
                    return func(state, value)
            else:
                return func(*param, **kwparam)

        if len(args) == 0:
            args = self.arguments.values
        if len(kwargs) == 0:
            kwargs = self.arguments.attribute_values
        else:
            _local_kwargs = copy.deepcopy(self.arguments.attribute_values)
            _local_kwargs.update(kwargs)
            kwargs = _local_kwargs
        return wrapper(self.function, args, kwargs)

    def resolve(self, arg, states=None, exchange=None):
        """
            >>> import checkmate.test_data
            >>> import sample_app.component_1.states
            >>> a = checkmate.test_data.App()
            >>> t = a.components['C1'].state_machine.transitions[1]
            >>> inc = t.incoming.factory()
            >>> states = [t.initial[0].factory()]
            >>> t.final[0].resolve('R', states=[states])
            Traceback (most recent call last):
            ...
            AttributeError
            >>> t.final[0].resolve('R', exchange=inc) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
        """
        if arg in self.resolve_logic.keys():
            (_type, _interface) = self.resolve_logic[arg]
            if _type in ['initial', 'final']:
                for _state in states:
                    if _interface.providedBy(_state):
                        return {arg: _state.value}
                raise AttributeError
            else:
                if _interface.providedBy(exchange):
                    if arg in iter(exchange.parameters):
                        if exchange.parameters[arg] is not None:
                            return {arg: exchange.parameters[arg]}
                    try:
                        return {arg: getattr(exchange, arg)}
                    except AttributeError:
                        raise AttributeError
                raise AttributeError
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
            >>> (ex.action, ex.parameters, ex.R)  # doctest: +ELLIPSIS
            ('AP', {'R': 1}, <sample_app.data_structure.ActionRequest object at ...
            >>> st.resolve('R', ex)  # doctest: +ELLIPSIS
            {'R': 1}

            >>> ex = st.factory()
            >>> (ex.action, ex.parameters, ex.R) # doctest: +ELLIPSIS
            ('AP', {'R': None}, <sample_app.data_structure.ActionRequest object at ...
            >>> st.resolve('R', ex)  # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
        """
        if arg in list(self.arguments.attribute_values.keys()):
            if arg in iter(exchange.parameters):
                if exchange.parameters[arg] is not None:
                    return {arg: exchange.parameters[arg]}
            try:
                return {arg: getattr(exchange, arg)}
            except AttributeError:
                raise AttributeError
        raise AttributeError

