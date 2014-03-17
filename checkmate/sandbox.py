import checkmate._tree


class Sandbox(object):
    def __init__(self, application):
        self.initial_application = application
        self.start()

    def start(self):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.exchanges
            >>> import sample_app.application
            >>> app = sample_app.application.TestData()
            >>> app.start()
            >>> out = app.components['C1'].process([sample_app.exchanges.AC()])
            >>> app.components['C1'].states[0].value
            'False'
            >>> box = checkmate.sandbox.Sandbox(app)
            >>> box.application.components['C1'].states[0].value
            'False'
        """
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
                    if done:
                        break
                if done:
                    break

    def __call__(self, transitions):
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
        is_run = False
        self.final = []
        self.initial = []
        for _transition in transitions:
            for component in list(self.application.components.values()):
                if not _transition in component.state_machine.transitions:
                    continue
                if len(_transition.incoming) > 0:
                    is_run = True
                    _incoming = _transition.generic_incoming(component.states)
                    _outgoing = component.process(_incoming)
                    self.exchanges = checkmate._tree.Tree(_incoming[0], [])
                elif len(_transition.outgoing) > 0:
                    is_run = True
                    _outgoing = component.simulate(_transition.outgoing[0].factory())
                    self.exchanges = checkmate._tree.Tree(_outgoing[0], [])
                else:
                    return False
                self.generate(_outgoing)
                self.exchanges = self.generate(_outgoing, self.exchanges)

            if is_run:
                for _initial in _transition.initial:
                    index = _transition.initial.index(_initial)
                    if _initial.code not in [_temp_init.code for _temp_init in self.initial]:
                        self.initial.append(_initial)
                    _final = _transition.final[index]
                    if _final.code not in [_temp_final.code for _temp_final in self.final]:
                        self.final.append(_final)
        return is_run

    def generate(self, exchanges, tree=None):
        """
            >>> import sample_app.application
            >>> import checkmate.sandbox
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> ex = sample_app.exchanges.AC()
            >>> ex.origin_destination('C2', 'C1')
            >>> box.generate([ex])
            >>> box.application.components['C3'].states[0].value
            'True'
        """
        for _exchange in exchanges:
            _outgoings = self.application.components[_exchange.destination].process([_exchange])
            if tree is not None:
                tree.add_node(checkmate._tree.Tree(_exchange, []))
            tree = self.generate(_outgoings, tree)
        return tree

