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
import checkmate.transition


class Run(checkmate._tree.Tree):
    def __init__(self, transition, nodes=None, states=None):
        assert type(transition) == checkmate.transition.Transition
        if nodes is None:
            nodes = []
        if states is None:
            states = []
        super(Run, self).__init__(transition, nodes)
        self._initial = None
        self._final = None
        self.itp_run = None
        self.change_states = []
        self.collected_run = None
        for f in transition.final:
            for s in states:
                if isinstance(s, f.partition_class):
                    self.change_states.append((type(s).__name__, s._dump()))
                    break

    @checkmate.fix_issue(
        'checkmate/issues/sandbox_call_notfound_transition.rst')
    def get_transition_by_input_states(self, exchanges, component):
        for _t in self.walk():
            if (_t in component.state_machine.transitions and
                _t.is_matching_incoming(exchanges, component.states) and
                    _t.is_matching_initial(component.states)):
                return _t

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
            if self.itp_run is not None:
                self._final = set(self.itp_run.root.final)

    def compare_initial(self, application):
        """"""
        for initial in self.initial:
            for component in application.components.values():
                if initial.match(component.states):
                    break
            else:
                return False
        return True

    @checkmate.fix_issue('checkmate/issues/compare_final.rst')
    @checkmate.fix_issue('checkmate/issues/sandbox_final.rst')
    @checkmate.fix_issue('checkmate/issues/validated_compare_states.rst')
    @checkmate.fix_issue("checkmate/issues/application_compare_states.rst")
    def compare_final(self, application, reference):
        """"""
        box = checkmate.sandbox.Sandbox(type(reference), reference)
        for run in self.breadthWalk():
            for name, component in application.components.items():
                _found = False
                if run.root in component.state_machine.transitions:
                    for final in run.root.final:
                        state = [_s for _s in
                                 box.application.components[name].states
                                 if isinstance(_s, final.partition_class)][0]
                        index = \
                            box.application.components[name].states.index(
                                state)
                        incoming = component.validation_dict.validated_items[
                            run.root]
                        _arguments = \
                            final.resolve(
                                box.application.components[name].states,
                                incoming, run.root.resolve_dict)
                        final.factory(instance=state, **_arguments)
                        if state == component.states[index]:
                            _found = True
                        else:
                            _found = False
                            break
                    else:
                        assert(_found or len(run.root.final) == 0)
                        _found = True
                else:
                    continue
                if _found:
                    break
            else:
                return False
        return True

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


@checkmate.report_issue('checkmate/issues/run_collect_multi_instances.rst')
@checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
@checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
@checkmate.report_issue('checkmate/issues/get_runs_from_failed_simulate.rst')
@checkmate.report_issue('checkmate/issues/execute_AP_R_AP_R2.rst')
def get_runs_from_application(_class):
    runs = []
    application = _class()
    application.start(default_state_value=False)
    origin_transitions = get_origin_transitions(application)
    sandbox = checkmate.sandbox.CollectionSandbox(_class, application)
    for _o in origin_transitions:
        run = Run(_o)
        sandbox.restart()
        for _run in sandbox(run):
            runs.append(_run)
    return runs


@checkmate.fix_issue('checkmate/issues/get_followed_runs.rst')
def followed_runs(application, run):
    runs = application.run_collection()
    length = len(runs)
    run_index = runs.index(run)
    followed_runs = []
    if application._runs_found[run_index]:
        current_row = [0]*length
        current_row[run_index] = 1
        _followed = numpy.matrix(current_row) * application._matrix
        _followed = _followed.tolist()[0]
        followed_runs = [t[1] for t in list(zip(_followed, runs)) if t[0] == 1]
        return followed_runs
    not_alike = []
    row = [0] * length
    for _i in run.final:
        not_alike.extend(_i.partition_class.not_alike(_i))
    not_alike_set = set(not_alike)
    for index, another_run in enumerate(runs):
        if (set([_i for _i in another_run.initial]).isdisjoint(not_alike_set) and
                another_run.compare_initial(application)):
            followed_runs.append(another_run)
            row[index] = 1
    application._matrix[run_index] = row
    application._runs_found[run_index] = True
    return followed_runs


@checkmate.fix_issue('checkmate/issues/collected_run_in_itp_run.rst')
def get_runs_from_transition(application, transition, itp_transition=False):
    runs = []
    transition_run = Run(transition)
    _class = type(application)
    if itp_transition:
        sandbox = checkmate.sandbox.CollectionSandbox(
                    _class, application, transition_run.walk())
    else:
        sandbox = checkmate.sandbox.CollectionSandbox(_class, application)
    initial = checkmate.sandbox.Sandbox(_class, sandbox.application)
    for _run in sandbox(transition_run, itp_run=itp_transition):
        for _r in sandbox.application.run_collection():
            if (_r.compare_initial(initial.application) and
                    set(_run.walk()).issubset(set(_r.walk()))):
                _run.collected_run = _r
                break
        runs.append(_run)
    return runs


@checkmate.fix_issue('checkmate/issues/get_origin_transitions.rst')
def get_origin_transitions(application):
    origin_transitions = []
    for _component in application.components.values():
        for _transition in _component.state_machine.transitions:
            if not len(_transition.incoming):
                origin_transitions.append(_transition)
            else:
                _incoming = _transition.generic_incoming(_component.states)
                for _c in application.components.values():
                    if _c == _component:
                        continue
                    if _c.get_transition_by_output(_incoming) is not None:
                        break
                else:
                    origin_transitions.append(_transition)
    return origin_transitions

