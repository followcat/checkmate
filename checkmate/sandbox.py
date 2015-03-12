# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate.runs
import checkmate.exception


class Sandbox(object):
    def __init__(self, application_class, application=None,
            initial_transitions=[]):
        self.application_class = application_class
        self.initial_application = application
        self.initial_transitions = initial_transitions
        self.start()

    @checkmate.fix_issue('checkmate/issues/sandbox_run_R2_itp_transition.rst')
    def start(self):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.exchanges
            >>> import sample_app.application
            >>> _cls = sample_app.application.TestData
            >>> c3 = _cls().components['C3']
            >>> transitions = [c3.state_machine.transitions[1]]
            >>> box = checkmate.sandbox.Sandbox(_cls,
            ...         initial_transitions=transitions)
            >>> box.application.components['C1'].states[0].value
            True
            >>> box.application.components['C3'].states[0].value
            True

            >>> app = _cls()
            >>> app.start()
            >>> out = app.components['C1'].process(
            ...         [sample_app.exchanges.Action('AC')])
            >>> app.components['C1'].states[0].value
            False
            >>> box = checkmate.sandbox.Sandbox(_cls, app)
            >>> box.application.components['C1'].states[0].value
            False
        """
        self.final = []
        self.initial = []
        self.transitions = None
        self.application = self.application_class()
        if self.initial_application is None:
            self.application.start()
            for outgoing in self.application.initializing_outgoing:
                for _o in outgoing:
                    for _d in _o.destination:
                        component = self.application.components[_d]
                        transitions = component.get_transitions_by_input([_o])
                        _run = checkmate.runs.Run(transitions[0], [])
                        if not self.__call__(_run):
                            raise \
                                RuntimeError("Applicaiton initializing Failed")
        else:
            self.application.start(
                self.initial_application.default_state_value)
            for component in self.application.components.values():
                for interface in [_d[0] for _d in 
                                  component.state_machine.states]:
                    done = False
                    for state in component.states:
                        if not interface.providedBy(state):
                            continue
                        init_components = self.initial_application.components
                        for init_state in \
                            init_components[component.name].states:
                            if not interface.providedBy(init_state):
                                continue
                            state.carbon_copy(init_state)
                            done = True
                            break
                        if done:
                            break
        
        for transition in self.initial_transitions:
            for initial in transition.initial:
                done = False
                for component in self.application.components.values():
                    for state in component.states:
                        if not initial.interface.providedBy(state):
                            continue
                        state.carbon_copy(
                            initial.factory(**initial.resolve()))
                        done = True
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
            >>> _cls = sample_app.application.TestData
            >>> box = checkmate.sandbox.Sandbox(_cls)
            >>> c1 = box.application.components['C1']
            >>> c1.states[0].value
            True
            >>> runs = box.application.run_collection
            >>> box(runs[0])
            True
            >>> box(runs[2])
            True
            >>> c1.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object ...
            >>> box.application.components['C3'].states[0].value
            False
        """
        _outgoing = []
        self.run = run
        self.transitions = None
        for component in self.application.components.values():
            _transitions = component.state_machine.transitions
            if not itp_run and not run.root in _transitions:
                continue
            if len(run.root.incoming) > 0:
                _incoming = run.root.generic_incoming(component.states)
                for _c in self.application.components.values():
                    _t = _c.get_transition_by_output(_incoming)
                    if _t is not None:
                        _outgoing = _c.simulate(_t)
                        self.transitions = _t
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
            self.transitions = \
                self.process(outgoing,
                    checkmate.runs.Run(self.transitions, []))
        except checkmate.exception.NoTransitionFound:
            self.transitions = None
        return self.is_run

    def process(self, exchanges, tree=None):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.application
            >>> _cls = sample_app.application.TestData
            >>> box = checkmate.sandbox.Sandbox(_cls)
            >>> ex = sample_app.exchanges.Action('AC')
            >>> ex.origin_destination('C2', 'C1')
            >>> runs = box.application.run_collection
            >>> c2 = box.application.components['C2']
            >>> _t = c2.get_transition_by_output([ex])
            >>> box.run = runs[0]
            >>> _run = checkmate.runs.Run(_t, [])
            >>> transitions = box.process([ex], _run)
            >>> box.application.components['C3'].states[0].value
            True
        """
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = self.application.components[_d]
                try:
                    _transition = \
                        self.run.get_transition_by_input_states([_exchange],
                            _c.states)
                except IndexError:
                    _transition = None
                _outgoings = _c.process([_exchange])
                if _transition is None:
                    continue
                tmp_run = self.process(_outgoings,
                            checkmate.runs.Run(_transition, []))
                tree.add_node(tmp_run)
        return tree

    def update_required_states(self, tree):
        """
        """
        transition = tree.root
        for index, _initial in enumerate(transition.initial):
            if _initial.interface not in [_i.interface for _i in self.initial]:
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
        try:
            tree = checkmate.runs.Run(self.transitions, [])
        except AssertionError:
            return []
        return self.process(self, outgoing, tree)

    def process(self, sandbox, exchanges, tree=None):
        split = False
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = sandbox.application.components[_d]
                _transitions = _c.get_transitions_by_input([_exchange])
                for _t in _transitions:
                    _app = sandbox.application
                    new_sandbox = Sandbox(type(_app), _app)
                    _c = new_sandbox.application.components[_d]
                    _outgoings = _c.process([_exchange], _t)
                    split_runs = \
                        self.process(new_sandbox, _outgoings,
                            checkmate.runs.Run(_t, [], states=_c.states))
                    for split, tmp_run in split_runs:
                        if len(_transitions) > 1 or split:
                            split = True
                            new_run = tree.copy()
                            new_run.add_node(tmp_run)
                            yield (split, new_run)
                        else:
                            tree.add_node(tmp_run)
        if split is False:
            yield (split, tree)

