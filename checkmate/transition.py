import sys

import zope.interface

import checkmate.state
import checkmate._utils

import checkmate._storage


class Transition(object):
    """Driving a change of state inside a state machine

        >>> import checkmate.test.data_state
        >>> import checkmate.test.data_exchange
        >>> t = Transition(incoming=[(checkmate.test.data_exchange.IAbsControlAction, 'TM()')])
        >>> t.incoming[0].function
        <unbound method AbsControlAction.TM>
    """
    def __init__(self, **argc):
        self.initial = []
        self.incoming = None
        self.final = []
        self.outgoing = []
        for item in ['initial', 'incoming', 'final', 'outgoing']:
            _attribute = getattr(self, item)
            if argc.has_key(item) == False:
                continue
            for _interface, _name in argc[item]:
                _o = checkmate._utils.get_class_implementing(_interface)
                _arguments, _kw_arguments = checkmate._utils.method_arguments(_name)

                if item in ['initial', 'final']:
                    getattr(self, item).append(checkmate._storage.store_state(_interface, _name))
                #elif item == 'final':
                #    self.final.append(checkmate._storage.store_state(_interface, _name))
                    #if checkmate._utils.method_basename(_name) is None:
                    #    self.final.append(checkmate._storage.store_state(_interface, _name))
#                        function = _o
#                        for input in self.initial:
#                            if input.code == _name:
#                                _arguments = input.arguments
#                                _function = input.function
#                        self.final.append(checkmate._storage.StateStorage(checkmate._utils.internal_code(_name), _interface,
#                                                _function, _arguments, kw_arguments=_kw_arguments))
                    #else:
                    #    self.final.append(checkmate._storage.StateStorage(checkmate._utils.internal_code(_name), _interface,
                    #                            getattr(_o, checkmate._utils.method_basename(_name)), _arguments, kw_arguments=_kw_arguments))
                elif item == 'incoming':
                    self.incoming = checkmate._storage.store_exchange(_interface, _name)
                elif item == 'outgoing':
                    #_list_args = []
                    #for _arg in _arguments:
                    #    _arg = _arg.lstrip()
                    #    for initial_state in self.initial:
                    #        _i_interface = initial_state.interface
                    #        _f = initial_state.function
                    #        if _f.__name__.rstrip('0') == _arg:
                    #            _list_args.append(_i_interface)
                    self.outgoing.append(checkmate._storage.store_exchange(_interface, _name))


    def is_matching_incoming(self, exchange):
        """
        """
        if self.incoming is not None:
            _interface = self.incoming.interface
            if _interface.providedBy(exchange):
                obj = self.incoming.factory()
                if exchange == obj:
                    return True
        return False

    def is_matching_initial(self, state_list):
        """
        """
        if len(self.initial) == 0:
            return True
        for _k in self.initial:
            _interface = _k.interface
            for _s in state_list:
                if _interface.providedBy(_s):
                    obj = _k.factory()
                    if _s == obj:
                        return True
        return False

    def resolve_arguments(self, type, data, states, incoming=None):
        resolved_arguments = {}
        entry = getattr(self, type)
        if type == 'incoming':
            arguments = entry.kw_arguments.keys()
        else:
            arguments = entry[entry.index(data)].kw_arguments.keys()
        for arg in arguments:
            found = None
            if type in ['final', 'incoming']:
                for item in self.initial:
                    if arg == item.code:
                        for _state in states:
                            if item.interface.providedBy(_state):
                                found = _state.value
                                break
                    if found is not None:
                        break
            if found is None:
                if type in ['final', 'outgoing']:
                    if arg in self.incoming.kw_arguments.keys():
                        found = getattr(incoming, arg)
            if found is None:
                if type in ['outgoing']:
                    for item in self.final:
                        if arg == item.code:
                            for _state in states:
                                if self.final.interface.providedBy(_state):
                                    found = _state.value
                                    break
                        if found is not None:
                            break
            if found is None:
                found = arg
            resolved_arguments[arg] = found
        return resolved_arguments

    def generic_incoming(self, states):
        arguments = self.resolve_arguments('incoming', self.incoming, states)
        return self.incoming.factory(kwargs=arguments)
        #try:
        #    arguments = self.resolve_arguments('incoming', self.incoming, states)
        #    return self.incoming.factory(kwargs=arguments)
        #except AttributeError:
        #    return checkmate.exchange.Exchange(None)
            
    def process(self, states, _incoming):
        def member_wrapper(cls, obj, args):
            return cls(obj, *args)

        for _state in states:
            for _interface in zope.interface.providedBy(_state):
                for _final in self.final:
                    if _final == None:
                        continue
                    _final_interface = _final.interface
                    if _final_interface == _interface:
                        if len(_final.kw_arguments) == 0:
                            _final.factory(args=[_state])
                        else:
                            resolved_arguments = self.resolve_arguments('final', _final, states, _incoming)
                            member_wrapper(_final.function, _state, resolved_arguments.values())
        _outgoing_list = []

        for outgoing_exchange in self.outgoing:
            resolved_arguments = self.resolve_arguments('outgoing', outgoing_exchange, states, _incoming)
            _outgoing_list.append(outgoing_exchange.factory(kwargs=resolved_arguments))
        return _outgoing_list

