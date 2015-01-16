import checkmate.runs
import checkmate.exception


class Sandbox(object):
    def __init__(self, application, initial_transitions=[]):
        self.initial_application = application
        self.initial_transitions = initial_transitions
        self.start()

    @checkmate.fix_issue('checkmate/issues/sandbox_run_R2_itp_transition.rst')
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
        self.application.start(self.initial_application.default_state_value)

        for component in self.application.components.values():
            for interface in [state_definition[0] for state_definition in component.state_machine.states]:
                done = False
                for state in component.states:
                    if not interface.providedBy(state):
                        continue
                    for initial_state in self.initial_application.components[component.name].states:
                        if not interface.providedBy(initial_state):
                            continue
                        state.carbon_copy(initial_state)
                        done = True
                        break
                    for transition in self.initial_transitions:
                    # if state not match self.initial_transitions[0]'s initial, the loop will break if done is True
                        for initial in transition.initial:
                            if not initial.interface.providedBy(state):
                                continue
                            state.carbon_copy(initial.factory(**initial.resolve()))
                            done = True
                            break
                        if done:
                            break
                    if done:
                        break

    @property
    def is_run(self):
        return self.transitions is not None

    def __call__(self, run, itp_run=False):
        """
            >>> import checkmate.sandbox
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> box.application.components['C1'].states[0].value
            'True'
            >>> runs = box.application.run_collection
            >>> box(runs[0])
            True
            >>> box(runs[2])
            True
            >>> box.application.components['C1'].states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> box.application.components['C3'].states[0].value
            'False'
        """
        _outgoing = []
        self.run = run
        self.transitions = None
        for component in self.application.components.values():
            if not itp_run and not run.root in component.state_machine.transitions:
                continue
            if len(run.root.incoming) > 0:
                _incoming = run.root.generic_incoming(component.states)
                for _c in self.application.components.values():
                    component_transition = _c.get_transition_by_output(_incoming)
                    if component_transition is not None:
                        _outgoing = _c.simulate(component_transition)
                        self.transitions = component_transition
                        break
                break
            elif len(run.root.outgoing) > 0:
                _outgoing = component.simulate(run.root)
                if len(_outgoing) == 0:
                    continue
                self.transitions = run.root
                break
        return self.run_process(_outgoing)

    def run_process(self, outgoing):
        if len(outgoing) == 0:
            return False
        try:
            self.transitions = self.process(outgoing, checkmate.runs.Run(self.transitions, []))
        except checkmate.exception.NoTransitionFound:
            self.transitions = None
        return self.is_run

    def process(self, exchanges, tree=None):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.application
            >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData())
            >>> ex = sample_app.exchanges.Action('AC')
            >>> ex.origin_destination('C2', 'C1')
            >>> runs = box.application.run_collection
            >>> _t = box.application.components['C2'].get_transition_by_output([ex])
            >>> box.run = runs[0]
            >>> transitions = box.process([ex], checkmate.runs.Run(_t, []))
            >>> box.application.components['C3'].states[0].value
            'True'
        """
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = self.application.components[_d]
                try:
                    _transition = self.run.get_transition_by_input_states([_exchange], _c.states)
                except IndexError:
                    _transition = None
                _outgoings = _c.process([_exchange])
                if _transition is None:
                    continue
                tmp_run = self.process(_outgoings, checkmate.runs.Run(_transition, []))
                tree.add_node(tmp_run)
        return tree

    def fill_procedure(self, procedure):
        if self.is_run:
            self.update_required_states(self.transitions)
            procedure.final = self.final
            procedure.initial = self.initial
            procedure.transitions = self.transitions

    def update_required_states(self, tree):
        """
        """
        transition = tree.root
        for index, _initial in enumerate(transition.initial):
            if _initial.interface not in [_temp_init.interface for _temp_init in self.initial]:
                self.initial.append(_initial)
                self.final.append(transition.final[index])
        for _node in tree.nodes:
            self.update_required_states(_node)


class CollectionSandbox(Sandbox):
    def __call__(self, run, itp_run=False):
        results = super(CollectionSandbox, self).__call__(run, itp_run)
        for _split, _run in results:
            if itp_run is True:
                _run.itp_run = run
            yield _run

    def run_process(self, outgoing):
        return self.process(self, outgoing, checkmate.runs.Run(self.transitions, []))

    def process(self, sandbox, exchanges, tree=None):
        split = False
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = sandbox.application.components[_d]
                _transitions = _c.get_transitions_by_input([_exchange])
                for _t in _transitions:
                    new_sandbox = Sandbox(sandbox.application)
                    _c = new_sandbox.application.components[_d]
                    _outgoings = _c.process([_exchange], _t)
                    for split, tmp_run in self.process(new_sandbox, _outgoings, checkmate.runs.Run(_t, [], states=_c.states)):
                        if len(_transitions) > 1 or split:
                            split = True
                            new_run = tree.copy()
                            new_run.add_node(tmp_run)
                            yield (split, new_run)
                        else:
                            tree.add_node(tmp_run)
        if split is False:
            yield (split, tree)
