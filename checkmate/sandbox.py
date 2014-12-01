import checkmate._tree
import checkmate.component


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
            >>> out = app.components['C1'].process([sample_app.exchanges.Action('AC')])
            >>> app.components['C1'].states[0].value
            'False'
            >>> box = checkmate.sandbox.Sandbox(app)
            >>> box.application.components['C1'].states[0].value
            'False'
        """
        self.final = []
        self.initial = []
        self.transitions = None
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
        return self.transitions is not None

    def __call__(self, transition, foreign_transitions=False):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> box.application.components['C1'].states[0].value
            'True'
            >>> box(sample_app.application.TestData().components['C1'].state_machine.transitions[0])
            True
            >>> box(sample_app.application.TestData().components['C3'].state_machine.transitions[1])
            True
            >>> box.application.components['C1'].states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> box.application.components['C3'].states[0].value
            'False'
        """
        _outgoing = []
        self.transitions = None
        for component in self.application.components.values():
            if not foreign_transitions and not transition in component.state_machine.transitions:
                continue
            if len(transition.incoming) > 0:
                _incoming = transition.generic_incoming(component.states)
                for _c in self.application.components.values():
                    component_transition = _c.get_transition_by_output(_incoming)
                    if component_transition is not None:
                        _outgoing = _c.simulate(component_transition)
                        self.transitions = component_transition
                        break
                break
            elif len(transition.outgoing) > 0:
                _outgoing = component.simulate(transition)
                if len(_outgoing) == 0:
                    continue
                self.transitions = transition
                break

        if len(_outgoing) == 0:
            return False
        self.transitions = self.process(_outgoing, checkmate._tree.Tree(self.transitions, []))
        if self.is_run:
            self.update_required_states(transition)
        return self.is_run

    def process(self, exchanges, tree=None):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> ex = sample_app.exchanges.Action('AC')
            >>> ex.origin_destination('C2', 'C1')
            >>> _t = box.application.components['C2'].get_transition_by_output([ex])
            >>> transitions = box.process([ex], checkmate._tree.Tree(_t, []))
            >>> box.application.components['C3'].states[0].value
            'True'
        """
        for _exchange in exchanges:
            for _des in _exchange.destination:
                _c = self.application.components[_des]
                _transition = _c.get_transition_by_input([_exchange])
                _outgoings = self.generate(_c, _exchange)
                if _outgoings is None:
                    if _exchange.return_code:
                        break
                    return None

                self.update_required_states(_transition)
                tmp_tree = self.process(_outgoings, checkmate._tree.Tree(_transition, []))
                if tmp_tree is None:
                    return None
                tree.add_node(tmp_tree)
        return tree

    def generate(self, component, _exchange):
        try:
            _outgoings = component.process([_exchange])
        except checkmate.component.NoTransitionFound:
            return None
        return _outgoings

    def fill_procedure(self, procedure):
        if self.is_run:
            procedure.final = self.final
            procedure.initial = self.initial
            procedure.transitions = self.transitions
            procedure.components = list(self.application.components.keys())

    def update_required_states(self, transition):
        """
        """
        for index, _initial in enumerate(transition.initial):
            if _initial.interface not in [_temp_init.interface for _temp_init in self.initial]:
                self.initial.append(_initial)
                self.final.append(transition.final[index])
