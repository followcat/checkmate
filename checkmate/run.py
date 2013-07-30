def itemize(initial, incoming, final, outgoing):
    filter_initial = []
    for s in initial:
        if s != final[initial.index(s)]:
            filter_initial.append((s.value, s.description()[0]))

    filter_final = []
    for s in final:
        if s != initial[final.index(s)]:
            filter_final.append((s.value, s.description()[0]))
    return (filter_initial, (incoming.action, incoming.description()[0]),
            filter_final, [(o.action, o.description()[0]) for o in outgoing])


class Run(object):
    """"""
    def __init__(self, initial, incoming, final, outgoing):
        """

            >>> import copy
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c1 = a.components['C1']
            >>> c1.start()
            >>> initial_state = copy.deepcopy(c1.states)
            >>> i = c1.state_machine.transitions[1].incoming.factory()
            >>> o = c1.state_machine.transitions[1].process(c1.states, i)
            >>> r = Run(initial_state, i, c1.states, o)
            >>> r.final
            [([{'R': None}], 'S-ANOST-02')]
        """
        # following lines cost 20sec in doctest
        #self.initial = initial
        #self.incoming = incoming
        #self.final = final
        #self.outgoing = outgoing
        self.itemized = itemize(initial, incoming, final, outgoing)
        self.initial = self.itemized[0]
        self.incoming = self.itemized[1]
        self.final = self.itemized[2]
        self.outgoing = self.itemized[3]
        self.desc_initial = [s.description()[2] for s in initial]
        self.desc_incoming = incoming.description()[2]
        self.desc_final = [s.description()[2] for s in final]
        self.desc_outgoing = [s.description()[2] for s in outgoing]

    def __eq__(self, other):
        return (self.itemized == other.itemized)

