import copy


def develop(state_machine, states, runs=[]):
    """Returns the list of possible runs
    """
    for transition in state_machine.transitions:
        if transition.is_matching_initial(states):
            local_runs = copy.deepcopy(runs)
            local_states = copy.deepcopy(states)

            incoming_exchange = transition.generic_incoming(local_states)
            transition.process(local_states, incoming_exchange)
            
            if ([s.value for s in states], (transition.incoming.code, incoming_exchange.description()[0]), [s.value for s in local_states]) not in local_runs:
                local_runs.append(([s.value for s in states], (transition.incoming.code, incoming_exchange.description()[0]), [s.value for s in local_states]))
                #runs.append(([s.value for s in states], transition.incoming.code, [s.value for s in local_states]))
                runs = develop(state_machine, local_states, local_runs)
    return runs

class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

