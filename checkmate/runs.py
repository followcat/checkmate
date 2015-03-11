import zope.interface

import checkmate._tree
import checkmate._visual
import checkmate.sandbox
import checkmate.exception
import checkmate.transition
import checkmate.interfaces


@zope.interface.implementer(checkmate.interfaces.IRun)
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
        self.followed_runs = None
        self.found_followed_runs = False
        self.change_states = []
        for f in transition.final:
            for s in states:
                if f.interface.providedBy(s):
                    self.change_states.append((type(s).__name__, s._dump()))
                    break

    def get_transition_by_input_states(self, exchanges, states):
        for _t in self.walk():
            if (_t.is_matching_initial(states) and
                    _t.is_matching_incoming(exchanges)):
                return _t
        else:
            raise checkmate.exception.NoTransitionFound

    def get_states(self):
        if self._initial is None or self._final is None:
            self._initial = []
            self._final = []
            for run in self.breadthWalk():
                for index, _initial in enumerate(run.root.initial):
                    if _initial.interface not in [_temp_init.interface for
                                                  _temp_init in self._initial]:
                        self._initial.append(_initial)
                        try:
                            _final = [_f for _f in run.root.final
                                      if _f.interface == _initial.interface][0]
                            _index = run.root.final.index(_final)
                            self._final.append(run.root.final[_index])
                        except IndexError:
                            pass
            if self.itp_run is not None:
                self._final = self.itp_run.root.final

    def compare_initial(self, application):
        """"""
        for run in self.breadthWalk():
            for component in application.components.values():
                if run.root in component.state_machine.transitions:
                    if run.root.is_matching_initial(component.states):
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
                                 if final.interface.providedBy(_s)][0]
                        index = \
                            box.application.components[name].states.index(
                                state)
                        incoming = \
                            component.validation_list.validated_items[
                                component.validation_list.transitions.index(
                                    run.root)]
                        _arguments = \
                            final.resolve(
                                box.application.components[name].states,
                                incoming)
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
            ...         sample_app.application.TestData())
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
            ...         sample_app.application.TestData())
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


@checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
@checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
@checkmate.fix_issue('checkmate/issues/get_runs_from_failed_simulate.rst')
@checkmate.report_issue('checkmate/issues/execute_AP_R_AP_R2.rst')
def get_runs_from_application(application):
    runs = []
    _class = type(application)
    application = _class()
    application.start(default_state_value=False)
    origin_transitions = get_origin_transitions(application)
    for _o in origin_transitions:
        sandbox = \
            checkmate.sandbox.CollectionSandbox(_class, application)
        run = checkmate.runs.Run(_o)
        for _run in sandbox(run):
            runs.append(_run)
    return runs


def get_runs_from_transition(application, transition, itp_transition=False):
    runs = []
    transition_run = checkmate.runs.Run(transition)
    _class = type(application)
    if itp_transition:
        sandbox = checkmate.sandbox.CollectionSandbox(
                    _class, application, transition_run.walk())
    else:
        sandbox = checkmate.sandbox.CollectionSandbox(_class, application)
    for _run in sandbox(transition_run, itp_run=itp_transition):
        runs.append(_run)
    return runs


@checkmate.report_issue(\
    'checkmate/issues/get_origin_transitions.rst', failed=2)
def get_origin_transitions(application):
    origin_transitions = []
    for _component in application.components.values():
        for _transition in _component.state_machine.transitions:
            if not len(_transition.incoming):
                origin_transitions.append(_transition)
    return origin_transitions

