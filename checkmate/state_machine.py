import copy

import checkmate.run


class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

    def develop(self, states, runs=[]):
        """Returns the list of possible runs

            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> r = c.state_machine.develop(c.states)
            >>> len(r)
            6
            >>> (r[0].initial, r[0].incoming, r[0].final)
            ([('True', 'S-STATE-01')], ('AC', 'X-ACTION-01'), [('False', 'S-STATE-02')])
            >>> (r[1].initial, r[1].incoming, r[1].final) # doctest: +ELLIPSIS
            ([([], 'S-ANOST-01')], ('AP', 'X-ACTION-02'), [([{'R': <sample_app.data_structure.ActionRequest object at ...
        """
        for transition in self.transitions:
            if transition.is_matching_initial(states):
                local_states = copy.deepcopy(states)

                try:
                    incoming_exchange = transition.generic_incoming(local_states)
                except AttributeError:
                    # Some transition have no incoming
                    incoming_exchange = checkmate.exchange.Exchange(None)
                outgoing_exchange_list = transition.process(local_states, incoming_exchange)
            
                this_run = checkmate.run.Run(states, incoming_exchange, local_states, outgoing_exchange_list)
                if this_run not in runs:
                    runs.append(this_run)
                    runs = self.develop(local_states, runs)
        return runs

