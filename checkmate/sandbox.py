
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
        for _transition in transitions:
            for component in list(self.application.components.values()):
                if not _transition in component.state_machine.transitions:
                    continue
                outgoings = component.process([incoming.factory() for incoming in _transition.incoming])
                if len(outgoings) > 0:
                    is_run = True
                self.generate(outgoings)
        return is_run

    def generate(self, exchanges):
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
            self.generate(_outgoings)

