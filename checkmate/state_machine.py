import copy

import checkmate.run


def itemize(initial, incoming, final, outgoing_list):
    return ([(s.value, s.description()[0]) for s in initial], (incoming.action, incoming.description()[0]),
            [(s.value, s.description()[0]) for s in final], [(o.action, o.description()[0]) for o in outgoing_list])


class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

    def develop(self, states, runs=[]):
        """Returns the list of possible runs
        """
        for transition in self.transitions:
            if transition.is_matching_initial(states):
                local_runs = copy.deepcopy(runs)
                local_states = copy.deepcopy(states)

                incoming_exchange = transition.generic_incoming(local_states)
                outgoing_exchange_list = transition.process(local_states, incoming_exchange)
            
                this_run = checkmate.run.Run(itemize(states, incoming_exchange, local_states, outgoing_exchange_list))
                if this_run not in local_runs:
                    local_runs.append(this_run)
                    #runs.append(([s.value for s in states], transition.incoming.code, [s.value for s in local_states]))
                    runs = self.develop(local_states, local_runs)
        return runs

