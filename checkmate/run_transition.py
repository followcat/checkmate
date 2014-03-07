import zope.interface

import checkmate.exchange

import checkmate.transition
import checkmate.component
import checkmate.application

def get_transition_list(application_class, exchanges, initial, transitions=None):
    """
        >>> import checkmate._storage
        >>> import checkmate.transition
        >>> import checkmate.application
        >>> import checkmate.run_transition
        >>> import sample_app.exchanges
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.start()
        >>> ex = sample_app.exchanges.AC()
        >>> states = []
        >>> for name in ['C1', 'C2', 'C3']:
        ...     states.extend(a.components[name].states)
        >>> transition_list = checkmate.run_transition.get_transition_list(sample_app.application.TestData, [ex], states, [])
        >>> (transition_list[0][0][0].value, transition_list[0][2][0].value)  # doctest: +ELLIPSIS
        ('True', ...
    """
    a = application_class()
    a.start()
    a.states = []
    return_transitions = []
    for component in list(a.components.values()):
        a.states.extend(component.states)
    init_states = []
    for state in initial:
        if type(state) == checkmate._storage.InternalStorage:
            init_states.append(state.factory())
        else:
            init_states.append(state)
    if not compare_states(a, init_states):
        #transform to initial
        if transitions is None:
            return None
        for transition in transitions:
            if compare_states(a, transition[0]):
                return_transitions.append(transition)
                exchange = transition[1][0]
                simulate_exchange(a, exchange)
            if compare_states(a, init_states):
                break
            else:
                continue
    if compare_states(a, init_states):
        #test exchange
        result = []
        simulate_exchange(a, exchanges[0])
        return_transitions.append([init_states, exchanges, a.states, []])
        return return_transitions
    else:
        return None
             
def simulate_exchange(application, exchange):
    for component in list(application.components.values()):
        if exchange.action in component.outgoings:
            for output in component.simulate(exchange):
                run(application, output)

def run(application, incoming):
    try:
        component = application.components[incoming.destination]
    except AttributeError as e:
        raise e("no component %s found in application" %incoming.destination)
    for output in component.process([incoming]):
        run(application, output)
    return
            
def compare_states(application, target):
        """"""
        matching = 0
        for _target in target:
            for _component in list(application.components.values()):
                try:
                    #Assume at most one state of component implements interface
                    _state = [_s for _s in _component.states if zope.interface.implementedBy(_target.__class__) == zope.interface.implementedBy(_s.__class__)].pop(0)
                    if _state == _target:
                        matching += 1
                        break
                    else:
                        break
                except IndexError:
                    continue
        return matching == len(target)