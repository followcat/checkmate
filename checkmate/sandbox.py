# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate.runs
import checkmate.exception


class Sandbox(object):
    def __init__(self, application_class, application=None,
            initial_blocks=[]):
        self.application_class = application_class
        self.initial_application = application
        self.initial_blocks = initial_blocks
        self.start()

    @checkmate.fix_issue('checkmate/issues/sandbox_run_R2_itp_transition.rst')
    def start(self):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.exchanges
            >>> import sample_app.application
            >>> _cls = sample_app.application.TestData
            >>> c3 = _cls().components['C3']
            >>> blocks = [c3.engine.blocks[1]]
            >>> box = checkmate.sandbox.Sandbox(_cls,
            ...         initial_blocks=blocks)
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
        self.used = False
        self.final = []
        self.initial = []
        self.blocks = None
        self.application = self.application_class()
        if self.initial_application is None:
            self.application.start()
            for outgoing in self.application.initializing_outgoing:
                for _o in outgoing:
                    for _d in _o.destination:
                        component = self.application.components[_d]
                        blocks = component.get_blocks_by_input([_o])
                        _run = checkmate.runs.Run(blocks[0], [])
                        if not self.__call__(_run):
                            raise \
                                RuntimeError("Applicaiton initializing Failed")
        else:
            self.application.start(
                self.initial_application.default_state_value)
            for component in self.initial_application.components.values():
                for index, state in enumerate(component.states):
                    self.application.components[component.name].states[index].\
                        carbon_copy(state)
        for block in self.initial_blocks:
            for initial in block.initial:
                done = False
                for component in self.application.components.values():
                    for state in component.states:
                        if not isinstance(state, initial.partition_class):
                            continue
                        state.carbon_copy(
                            initial.factory(**initial.resolve()))
                        done = True
                        break
                    if done:
                        break

    def restart(self):
        if self.used is True:
            self.start()

    @property
    def is_run(self):
        return (self.blocks is not None and
                set(self.run.walk()).issubset(set(self.blocks.walk())))

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
            >>> runs = box.application.run_collection()
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
        self.blocks = None
        for component in self.application.components.values():
            _blocks = component.engine.blocks
            if not itp_run and run.root not in _blocks:
                continue
            if len(run.root.incoming) > 0:
                _incoming = run.root.generic_incoming(component.states)
                for _c in self.application.components.values():
                    if _c == component:
                        continue
                    _b = _c.get_blocks_by_output(_incoming)
                    if _b is not None:
                        _outgoing = _c.simulate(_b)
                        self.blocks = _b
                        break
                if self.blocks is not None:
                    break
            _outgoing = component.simulate(run.root)
            self.blocks = run.root
            break
        return self.run_process(_outgoing)

    def run_process(self, outgoing):
        try:
            self.blocks = \
                self.process(outgoing,
                    checkmate.runs.Run(self.blocks, []))
        except checkmate.exception.NoBlockFound:
            self.blocks = None
        return self.is_run

    def process(self, exchanges, tree=None):
        """
            >>> import checkmate.sandbox
            >>> import sample_app.application
            >>> _cls = sample_app.application.TestData
            >>> box = checkmate.sandbox.Sandbox(_cls)
            >>> ex = sample_app.exchanges.Action('AC')
            >>> ex.origin_destination('C2', 'C1')
            >>> runs = box.application.run_collection()
            >>> c2 = box.application.components['C2']
            >>> _b = c2.get_blocks_by_output([ex])
            >>> box.run = runs[0]
            >>> _run = checkmate.runs.Run(_b, [])
            >>> blocks = box.process([ex], _run)
            >>> box.application.components['C3'].states[0].value
            True
        """
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = self.application.components[_d]
                _transition = self.run.get_block_by_input_states(
                    [_exchange], _c)
                if _transition is None:
                    continue
                _outgoings = _c.process([_exchange])
                tmp_run = self.process(_outgoings,
                            checkmate.runs.Run(_transition, []))
                tree.add_node(tmp_run)
        return tree

    def update_required_states(self, tree):
        """
        """
        block = tree.root
        for index, _initial in enumerate(block.initial):
            if _initial.partition_class not in [_i.partition_class
                                                for _i in self.initial]:
                self.initial.append(_initial)
                self.final.append(block.final[index])
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
            tree = checkmate.runs.Run(self.blocks, [])
        except AssertionError:
            return []
        return self.process(self, outgoing, tree)

    def process(self, sandbox, exchanges, tree=None):
        split = False
        for _exchange in exchanges:
            for _d in _exchange.destination:
                _c = sandbox.application.components[_d]
                _blocks = _c.get_blocks_by_input([_exchange])
                for _b in _blocks:
                    if _b == tree.root:
                        continue
                    self.used = True
                    _app = sandbox.application
                    new_sandbox = Sandbox(type(_app), _app)
                    _c = new_sandbox.application.components[_d]
                    _outgoings = _c.process([_exchange], _b)
                    _run = checkmate.runs.Run(_b, [], states=_c.states,
                                                exchanges=[_exchange])
                    split_runs = self.process(new_sandbox, _outgoings, _run)
                    for split, tmp_run in split_runs:
                        if len(_blocks) > 1 or split:
                            split = True
                            new_run = tree.copy()
                            new_run.add_node(tmp_run)
                            yield (split, new_run)
                        else:
                            tree.add_node(tmp_run)
        if split is False:
            yield (split, tree)

