
class Sandbox(object):
    def __init__(self, application_class, initial_transitions=[], initial_application=None):
        self.application_class = application_class
        self.initial_application = initial_application
        self.initial_transitions = initial_transitions
        self.start()

    def start(self):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.exchanges
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData,
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
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData,
            ...                                 initial_application=app)
            >>> box.application.components['C1'].states[0].value
            'False'
        """
        self.application = self.application_class()
        self.application.start()

        if isinstance(self.initial_application, self.application_class):
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

        for component in self.application.components.values():
            done = False
            for transition in self.initial_transitions:
                if transition not in component.state_machine.transitions:
                    continue
                for initial in transition.initial:
                    for state in component.states:
                        if initial.interface.providedBy(state):
                            state.value = initial.factory().value
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
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData)
            >>> box.start()
            >>> box([sample_app.application.TestData().components['C1'].state_machine.transitions[0],
            ...      sample_app.application.TestData().components['C3'].state_machine.transitions[1]])
            >>> box.application.components['C1'].states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> box.application.components['C3'].states[0].value
            'False'
        """
        for _transition in transitions:
            for component in list(self.application.components.values()):
                if not _transition in component.state_machine.transitions:
                    continue
                outgoings = component.process([incoming.factory() for incoming in _transition.incoming])
                self.generate(outgoings)

    def generate(self, exchanges):
        """
            >>> import sample_app.application
            >>> import checkmate.sandbox
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData)
            >>> box.start()
            >>> ex = sample_app.exchanges.AC()
            >>> ex.origin_destination('C2', 'C1')
            >>> box.generate([ex])
            >>> box.application.components['C3'].states[0].value
            'True'
        """
        for _exchange in exchanges:
            _outgoings = self.application.components[_exchange.destination].process([_exchange])
            self.generate(_outgoings)

