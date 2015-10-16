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
                        _run = checkmate.runs.Run(blocks[0], [],
                                exchanges=[_o])
                        if not self.__call__(_run.exchanges):
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
        return self.blocks is not None

    def __call__(self, exchanges, itp_run=False):
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
            >>> box(runs[0].exchanges)
            True
            >>> box(runs[1].exchanges)
            True
            >>> c1.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object ...
            >>> box.application.components['C3'].states[0].value
            False
        """
        _outgoing = []
        self.blocks = None
        _states = None
        if exchanges is None or len(exchanges) == 0:
            return self.is_run
        for component in self.application.components.values():
            start_blocks = component.get_blocks_by_input(exchanges)
            if len(start_blocks) > 0:
                break
        else:
            return self.is_run
        self.used = True
        _outgoing = component.process(exchanges)
        _states = component.copy_states()
        self.blocks = start_blocks[0]
        return self.run_process(_outgoing, _states, exchanges)

    def run_process(self, outgoing, states, exchanges):
        if self.blocks is None:
            return False
        try:
            self.blocks = \
                self.process(outgoing,
                    checkmate.runs.Run(self.blocks, [], states, exchanges))
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
                blocks = _c.get_blocks_by_input([_exchange])
                _outgoings = _c.process([_exchange])
                exchange = type(_exchange)()
                exchange.carbon_copy(_exchange)
                exchange.origin_destination(_exchange.origin, [_d])
                states = _c.copy_states()
                tmp_run = self.process(_outgoings,
                            checkmate.runs.Run(blocks[0], [],
                                states=states, exchanges=[exchange]))
                tree.add_node(tmp_run)
        return tree

