import copy

def itemize(initial, incoming, final, outgoing_list):
    return ([s.value for s in initial], (incoming.action, incoming.description()[0]),
            [s.value for s in final], [(o.action, o.description()[0]) for o in outgoing_list])

def develop(state_machine, states, runs=[]):
    """Returns the list of possible runs
    """
    for transition in state_machine.transitions:
        if transition.is_matching_initial(states):
            local_runs = copy.deepcopy(runs)
            local_states = copy.deepcopy(states)

            incoming_exchange = transition.generic_incoming(local_states)
            outgoing_exchange_list = transition.process(local_states, incoming_exchange)
            
            if itemize(states, incoming_exchange, local_states, outgoing_exchange_list) not in local_runs:
                local_runs.append(itemize(states, incoming_exchange, local_states, outgoing_exchange_list))
                #runs.append(([s.value for s in states], transition.incoming.code, [s.value for s in local_states]))
                runs = develop(state_machine, local_states, local_runs)
    return runs

class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

