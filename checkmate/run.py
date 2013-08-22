def itemize(initial, incoming, final, outgoing):
    filter_initial = []
    for s in initial:
        if s != final[initial.index(s)]:
            filter_initial.append((s.value, s.description()[0]))
    #filter_initial = [(s.value, s.description()[0]) for s in initial]

    filter_final = []
    for s in final:
        if s != initial[final.index(s)]:
            filter_final.append((s.value, s.description()[0]))
    #filter_final = [(s.value, s.description()[0]) for s in final]
    return (filter_initial, [(i.action, i.description()[0]) for i in incoming],
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
            >>> i = c1.state_machine.transitions[1].incoming[0].factory()
            >>> o = c1.state_machine.transitions[1].process(c1.states, [i])
            >>> r = Run(initial_state, [i], c1.states, o)
            >>> r.itemized[2] # doctest: +ELLIPSIS
            [([{'R': <sample_app.data_structure.ActionRequest object at ...
        """
        self.initial = initial
        self.incoming = incoming
        self.final = final
        self.outgoing = outgoing

        # Cache for fast comparison of two runs
        self.itemized = itemize(initial, incoming, final, outgoing)

    @property
    def desc_initial(self):
        return [s.description()[2] for s in self.initial]
    @property
    def desc_incoming(self):
        return [s.description()[2] for s in self.incoming]

    @property
    def desc_final(self):
        return [s.description()[2] for s in self.final]

    @property
    def desc_outgoing(self):
        return [s.description()[2] for s in self.outgoing]

    def __eq__(self, other):
        return (self.itemized == other.itemized)

