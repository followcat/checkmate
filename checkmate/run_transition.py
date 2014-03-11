import zope.interface

import checkmate.path_transition

def get_transition_list(application_class, exchanges, initial, transitions=None):
    """
        >>> import sample_app.exchanges
        >>> import sample_app.application
        >>> import checkmate.run_transition
        >>> a = sample_app.application.TestData()
        >>> a.start()
        >>> exchanges = [sample_app.exchanges.AC(), sample_app.exchanges.RE(), sample_app.exchanges.ARE(), sample_app.exchanges.AP(), sample_app.exchanges.DA()]
        >>> states = []
        >>> for name in ['C1', 'C2', 'C3']:
        ...     states.extend(a.components[name].states)
        >>> transition_list = checkmate.run_transition.get_transition_list(sample_app.application.TestData, exchanges, states, [])
        >>> (transition_list[0].initial[0].value, transition_list[0].final[0].value)  # doctest: +ELLIPSIS
        ('True', ...
    """
    a = application_class()
    a.start()
    states = []
    return_transitions = []
    for component in list(a.components.values()):
        states.extend(component.states)
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
        previous = []
        found = False
        current = init_states
        for i in (range(-1, -1-len(transitions), -1)):
            transition = transitions[i]
            if transition.is_matching_final(current):
                previous.append(transition)
                return_transitions.insert(0, transition)
                current = transition.initial
                if transition.is_matching_initial(states):
                    found = True
                    break
            else:
                continue
        if found:
            for i in range(len(return_transitions)):
                transition = return_transitions[i]
                simulate_exchange(a, transition.incoming[0])
        else:
            return None
    if compare_states(a, init_states):
        simulate_exchange(a, exchanges[0])
        transition = checkmate.path_transition.Path_Transition(initial=init_states, incoming=exchanges, final=states, outgoing=[])
        if transitions is not None:
            for _t in transitions:
                if transition.is_matching_initial(_t.final):
                    transition.previous_transitions.append(_t)
                if transition.is_matching_final(_t.initial):
                    transition.next_transitions.append(_t)
        return_transitions.append(transition)
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
