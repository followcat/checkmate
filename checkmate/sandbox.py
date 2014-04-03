import checkmate._tree


class Sandbox(object):
    def __init__(self, application, initial_transitions=[]):
        self.initial_application = application
        self.initial_transitions = initial_transitions
        self.start()

    def start(self):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.exchanges
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData(),
            ...                                 [sample_app.application.TestData().components['C3'].state_machine.transitions[1]])
            >>> box.application.components['C1'].states[0].value
            'True'
            >>> box.application.components['C3'].states[0].value
            'True'

            >>> app = sample_app.application.TestData()
            >>> app.start()
            >>> out = app.components['C1'].process([sample_app.exchanges.AC()])
            >>> app.components['C1'].states[0].value
            'False'
            >>> box = checkmate.sandbox.Sandbox(app)
            >>> box.application.components['C1'].states[0].value
            'False'
        """
        self.final = []
        self.initial = []
        self.exchanges = None
        self.application = type(self.initial_application)()
        self.application.start()

        for component in self.application.components.values():
            done = False
            for interface in [state_definition[0] for state_definition in component.state_machine.states]:
                for state in component.states:
                    if not interface.providedBy(state):
                        continue
                    for initial_state in self.initial_application.components[component.name].states:
                        if not interface.providedBy(initial_state):
                            continue
                        state.value = initial_state.value
                        done = True
                        break
                    for transition in self.initial_transitions:
                        for initial in transition.initial:
                            if not initial.interface.providedBy(state):
                                continue
                            state.value = initial.factory().value
                            done = True
                            break
                        if done:
                            break
                    if done:
                        break

    @property
    def is_run(self):
        return self.exchanges is not None

    def __call__(self, transitions, foreign_transitions=False):
        """
            >>> import sample_app.application
            >>> import checkmate.sandbox
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> box.application.components['C1'].states[0].value
            'True'
            >>> box([sample_app.application.TestData().components['C1'].state_machine.transitions[0],
            ...      sample_app.application.TestData().components['C3'].state_machine.transitions[1]])
            True
            >>> box.application.components['C1'].states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> box.application.components['C3'].states[0].value
            'False'
        """
        for _transition in transitions:
            _outgoing = []
            if len(_transition.incoming) > 0:
                #try simulation by any component first
                for component in list(self.application.components.values()):
                    if not foreign_transitions and not _transition in component.state_machine.transitions:
                        continue
                    _incoming = _transition.generic_incoming(component.states)
                    _outgoing = component.simulate(_incoming[0])
                    if len(_outgoing) == 0:
                        #simulation failed
                        continue
                    break
                if len(_outgoing) == 0:
                    for component in list(self.application.components.values()):
                        if not foreign_transitions and not _transition in component.state_machine.transitions:
                            continue
                        _incoming = _transition.generic_incoming(component.states)
                        _outgoing = component.process([_incoming[0]])
                        if len(_outgoing) == 0:
                            continue
                        self.exchanges = checkmate._tree.Tree(_incoming[0], [])
                        break
            #for now, this is not a real empty incoming but the root of TransitionTree
            elif len(_transition.outgoing) > 0:
                for component in list(self.application.components.values()):
                    if not foreign_transitions and not _transition in component.state_machine.transitions:
                        continue
                    _outgoing = component.simulate(_transition.outgoing[0].factory())
                    if len(_outgoing) == 0:
                        continue
                    break
            if len(_outgoing) == 0:
                return False

            self.exchanges = self.generate(_outgoing, self.exchanges)

            if self.is_run:
                self.update_required_states(_transition)
        return self.is_run

    def generate(self, exchanges, tree=None):
        """
            >>> import sample_app.application
            >>> import checkmate.sandbox
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> ex = sample_app.exchanges.AC()
            >>> ex.origin_destination('C2', 'C1')
            >>> exchanges = box.generate([ex])
            >>> box.application.components['C3'].states[0].value
            'True'
        """
        i = 0
        for _exchange in exchanges:
            _transition = self.application.components[_exchange.destination].get_transition_by_input([_exchange])
            _outgoings = self.application.components[_exchange.destination].process([_exchange])
            if len(_outgoings) == 0 and self.application.components[_exchange.destination].transition_not_found:
                continue
            self.update_required_states(_transition)
            if tree is None:
                tree = checkmate._tree.Tree(_exchange, [])
                tree = self.generate(_outgoings, tree)
                self.exchanges = tree
            else:
                tree.add_node(checkmate._tree.Tree(_exchange, []))
                tree.nodes[i] = self.generate(_outgoings, tree.nodes[i])
                i += 1
        return tree

    def fill_procedure(self, procedure):
        if self.is_run:
            procedure.initial = self.initial
            procedure.exchanges = self.exchanges
            procedure.components = list(self.application.components.keys())

    def update_required_states(self, transition):
        for _initial in transition.initial:
            index = transition.initial.index(_initial)
            if _initial.code not in [_temp_init.code for _temp_init in self.initial]:
                self.initial.append(_initial)
            _final = transition.final[index]
            if _final.code not in [_temp_final.code for _temp_final in self.final]:
                self.final.append(_final)

