import copy

import checkmate.run


class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

    def develop(self, states, runs):
        """Returns the list of possible runs

            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> r = c.state_machine.develop(c.states, [])
            >>> len(r)
            6
            >>> (r[0].itemized[0], r[0].itemized[1], r[0].itemized[2])
            ([('True', 'S-STATE-01')], [('AC', 'X-ACTION-01')], [('False', 'S-STATE-02')])
            >>> (r[1].itemized[0], r[1].itemized[1], r[1].itemized[2]) # doctest: +ELLIPSIS
            ([([], 'S-ANOST-01')], [('AP', 'X-ACTION-02')], [([{'R': <sample_app.data_structure.ActionRequest object at ...
        """
        for transition in self.transitions:
            if transition.is_matching_initial(states):
                local_states = copy.deepcopy(states)

                incoming = transition.generic_incoming(local_states)
                outgoing = transition.process(local_states, incoming)
            
                this_run = checkmate.run.Run(states, incoming, local_states, outgoing)
                if this_run not in runs:
                    runs.append(this_run)
                    runs = self.develop(local_states, runs)
        return runs

