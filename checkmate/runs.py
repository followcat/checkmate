# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import numpy

import checkmate._tree
import checkmate._visual
import checkmate.sandbox
import checkmate.exception
import checkmate.tymata.transition


class Run(checkmate._tree.Tree):
    def __init__(self, block, nodes=None, states=None, exchanges=None):
        assert isinstance(block, checkmate.tymata.transition.Block)
        if nodes is None:
            nodes = []
        if states is None:
            states = ()
        if exchanges is None:
            exchanges = ()
        super(Run, self).__init__(block, nodes)
        self.exchanges = exchanges
        self._initial = None
        self._final = None
        self.itp_run = None
        self._collected_box = None
        self.itp_final = []
        self.change_states = []
        self.validate_items = (tuple(exchanges), tuple(states))
        self._collected_run = None
        for f in block.final:
            for s in states:
                if isinstance(s, f.partition_class):
                    self.change_states.append((type(s).__name__, s._dump()))
                    break

    @property
    def collected_run(self):
        if self._collected_box is not None:
            for _r in self._collected_box.application.run_collection():
                if _r.compare_initial(self._collected_box.application) and \
                    set(self.walk()).issubset(set(_r.walk())):
                    self._collected_run = _r
                    break
        return self._collected_run
 
    @checkmate.fix_issue(
        'checkmate/issues/sandbox_call_notfound_transition.rst')
    def get_block_by_input_states(self, exchanges, component):
        for _b in self.walk():
            if (_b in component.engine.blocks and
                _b.is_matching_incoming(exchanges, component.states) and
                    _b.is_matching_initial(component.states)):
                return _b

    def get_validate_items_by_input(self, exchanges):
        items = []
        for run in self.breadthWalk():
            for _e in exchanges:
                if _e not in run.exchanges:
                    break
            else:
                items.append(run.validate_items)
        return items

    def get_states(self):
        if self._initial is None or self._final is None:
            initial_dict = dict()
            final_dict = dict()
            for run in self.breadthWalk():
                for index, _initial in enumerate(run.root.initial):
                    if _initial.partition_class not in initial_dict:
                        initial_dict[_initial.partition_class] = _initial
                    final_dict[_initial.partition_class] = _initial
                for index, _final in enumerate(run.root.final):
                    final_dict[_final.partition_class] = _final
            self._initial = set(initial_dict.values())
            self._final = set(final_dict.values())
            if len(self.itp_final):
                self._final = set(self.itp_final)

    def compare_initial(self, application):
        """"""
        box = checkmate.sandbox.Sandbox(type(application), application)
        if self.collected_run is not None:
            exchanges = self.collected_run.exchanges
        else:
            exchanges = self.exchanges
        return box(exchanges) and \
                set(self.walk()).issubset(set(box.blocks.walk()))

    @checkmate.fix_issue('checkmate/issues/compare_final.rst')
    @checkmate.fix_issue('checkmate/issues/sandbox_final.rst')
    @checkmate.fix_issue('checkmate/issues/validated_compare_states.rst')
    @checkmate.fix_issue("checkmate/issues/application_compare_states.rst")
    def compare_final(self, application):
        """"""
        final = {}
        for run in self.breadthWalk():
            for state in run.validate_items[1]:
                final[type(state)] = state
        matched = 0
        for state in final.values():
            for c in application.components.values():
                if state in c.states:
                    matched += 1
                    break
        if matched == len(final):
            return True
        return False

    def copy(self):
        _run = super().copy()
        _run.exchanges = self.exchanges
        _run.validate_items = self.validate_items
        return _run

    def add_node(self, tree):
        self._initial = None
        self._final = None
        super().add_node(tree)

    def visual_dump_initial(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.get_runs_from_application(
            ...         sample_app.application.TestData)
            >>> states = src[0].visual_dump_initial()
            >>> states['C1']['State']['value']
            True
            >>> states['C3']['Acknowledge']['value']
            False
        """
        state_dict = {}
        for run in self.breadthWalk():
            for _s in run.root.initial:
                if run.root.owner not in state_dict:
                    state_dict[run.root.owner] = {}
                state = _s.factory()
                cls_name = type(state).__name__
                if cls_name not in state_dict:
                    state_dict[run.root.owner][cls_name] = state._dump()
        return state_dict

    def visual_dump_final(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.get_runs_from_application(
            ...         sample_app.application.TestData)
            >>> states = src[0].visual_dump_final()
            >>> states['C1']['State']['value']
            False
            >>> states['C3']['Acknowledge']['value']
            True
        """
        state_dict = {}
        for run in self.breadthWalk():
            for state in run.change_states:
                if run.root.owner not in state_dict:
                    state_dict[run.root.owner] = {}
                state_dict[run.root.owner][state[0]] = state[1]
        return state_dict

    def visual_dump_steps(self):
        dump_dict = {}
        dump_dict['root'] = self.root.name
        dump_dict['incoming'] = [i.origin_code for i in self.root.incoming]
        dump_dict['outgoing'] = [o.origin_code for o in self.root.outgoing]
        dump_dict['states'] = {self.root.owner: dict(self.change_states)}
        dump_dict['nodes'] = []
        for element in self.nodes:
            dump_dict['nodes'].append(element.visual_dump_steps())
        return dump_dict

    @property
    def initial(self):
        self.get_states()
        return self._initial

    @property
    def final(self):
        self.get_states()
        return self._final

    def final_alike(self):
        final_alike = set()
        for _f in self.final:
            alike = _f.partition_class.alike(_f, self.initial)
            if alike is not None:
                final_alike.add(alike)
        return final_alike


@checkmate.report_issue('checkmate/issues/run_collect_multi_instances.rst')
@checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
@checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
@checkmate.fix_issue('checkmate/issues/get_runs_from_failed_simulate.rst')
@checkmate.report_issue('checkmate/issues/execute_AP_R_AP_R2.rst', failed=4)
def get_runs_from_application(_class):
    runs = []
    application = _class()
    application.start()
    origin_exchanges = _class.origin_exchanges()
    generate_run(application, runs, [], origin_exchanges)
    return runs


def generate_run(application, runs, exchange_states, exchanges):
    entrances = []
    for _ex in exchanges:
        if (_ex, application.state_list()) in exchange_states:
            continue
        box = checkmate.sandbox.Sandbox(type(application), application)
        states = application.copy_states()
        exchange_states.append((_ex, states))
        if box([_ex]) and box.blocks not in runs:
            runs.append(box.blocks)
            entrances.append(box)
    for box in entrances:
        generate_run(box.application, runs, exchange_states, exchanges) 


@checkmate.fix_issue('checkmate/issues/get_followed_runs.rst')
def followed_runs(application, run):
    runs = application.run_collection()
    length = len(runs)
    run_index = runs.index(run)
    followed_runs = []
    if application._runs_found[run_index]:
        followed_runs = [runs[i] for i in application._matrix[run_index]
                         .nonzero()[1].tolist()[0]]
        return followed_runs
    row = [0] * length
    alike_set = set()
    partition_class_set = set()
    for _f in run.final:
        alike = _f.partition_class.alike(_f, run.initial)
        if alike is not None:
            alike_set.add(alike)
            partition_class_set.add(_f.partition_class)
    for index, another_run in enumerate(runs):
        select_parititon = set()
        for _i in another_run.initial:
            if _i.partition_class in partition_class_set:
                select_parititon.add(_i)
        if select_parititon.issubset(alike_set):
            followed_runs.append(another_run)
            row[index] = 1
    application._matrix[run_index] = row
    application._runs_found[run_index] = True
    return followed_runs


@checkmate.fix_issue('checkmate/issues/collected_run_in_itp_run.rst')
def get_runs_from_transition(application, transition, itp_transition=False):
    runs = []
    exchanges = []
    _class = type(application)
    box = checkmate.sandbox.Sandbox(_class, application, [transition])
    _incoming = transition.generic_incoming(box.application.state_list())
    origin = ''
    destination = []
    for _c in box.application.components.values():
        if _c.get_blocks_by_output(_incoming) is not None:
            origin = _c.name
        if len(_c.get_blocks_by_input(_incoming)) > 0:
            if _c.name not in destination:
                destination.append(_c.name)
    for _exchange in _incoming: 
        _exchange.origin_destination(origin, destination)
        exchanges.append(_exchange)
    assert box(exchanges)
    _run = box.blocks
    initial = checkmate.sandbox.Sandbox(_class, application, [transition])
    if itp_transition:
        _run.itp_final = transition.final
        _run._collected_box = initial
    runs.append(_run)
    return runs


@checkmate.fix_issue('checkmate/issues/get_origin_transitions.rst')
def get_origin_transitions(application):
    origin_transitions = []
    for _component in application.components.values():
        for _transition in _component.engine.blocks:
            if not len(_transition.incoming):
                origin_transitions.append(_transition)
            else:
                _incoming = _transition.generic_incoming(_component.states)
                for _c in application.components.values():
                    if _c == _component:
                        continue
                    if _c.get_blocks_by_output(_incoming) is not None:
                        break
                else:
                    origin_transitions.append(_transition)
    return origin_transitions


def get_origin_exchanges(application_class):
    """
        >>> import sample_app.application
        >>> import checkmate.runs
        >>> cls = sample_app.application.TestData
        >>> exchanges = checkmate.runs.get_origin_exchanges(cls)
        >>> [_e.value for _e in exchanges]
        ['PBAC', 'PBRL', 'PBPP']
    """
    incomings = []
    outgoings = []
    origin_exchanges = []
    application = application_class()
    application.start()
    for _component in application.components.values():
        for _block in _component.engine.blocks:
            incomings.extend(_block.incoming)
            outgoings.extend(_block.outgoing)
    for _incoming in incomings:
        for _o in outgoings:
            if _incoming.partition_class == _o.partition_class:
                break
        else:
            _i = _incoming.factory(**_incoming.resolve())
            for _e in _component.exchange_destination(_i):
                origin_exchanges.append(_e)
    return origin_exchanges


def find_next_runs(application, exchanges, current_run=None):
    """
    3 conditions:
        1. we find next runs by matrix
        2. current_run is None, find next runs by exchanges
        3. find next runs by exchanges and update matrix
    >>> import sample_app.application
    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> app = sample_app.application.TestData
    >>> exchanges = app.origin_exchanges()
    >>> box = checkmate.sandbox.Sandbox(app)
    >>> runs = app.run_collection()
    >>> next_runs = checkmate.runs.find_next_runs(box.application,
    ...     exchanges, None)
    >>> next_runs[0].validate_items[0][0].value
    'PBAC'
    >>> box(next_runs[0].exchanges)
    True
    >>> next_runs = checkmate.runs.find_next_runs(box.application,
    ...     exchanges, next_runs[0])
    >>> next_runs[0].validate_items[0][0].value
    'PBRL'
    """
    _class = type(application)
    runs = application.run_matrix_index
    next_runs = []
    if current_run is not None and current_run in runs:
        _index = runs.index(current_run)
        if application.run_matrix_tag[_index]:
            return [runs[i] for i in
                application.run_matrix[_index].nonzero()[1].tolist()[0]]
    for _exchange in exchanges:
        box = checkmate.sandbox.Sandbox(_class, application)
        if box([_exchange]):
            _run = box.blocks
            next_runs.append(_run)
    if current_run is None:
        return next_runs
    if current_run not in runs:
        runs.append(current_run)
    application.update_matrix(next_runs, current_run)
    return next_runs

