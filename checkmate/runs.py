import zope.interface

import checkmate._tree
import checkmate._visual
import checkmate.sandbox
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
        self.itp_transition = None
        self.change_states = []
        for f in transition.final:
            for s in states:
                if f.interface.providedBy(s):
                    self.change_states.append((type(s).__name__, s._dump()))
                    break

    def visual_dump_initial(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.get_runs_from_application(sample_app.application.TestData())
            >>> states = src[0].visual_dump_initial()
            >>> states['C1']['State']['value'], states['C3']['Acknowledge']['value']
            ('True', 'False')
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
            >>> src = checkmate.runs.get_runs_from_application(sample_app.application.TestData())
            >>> states = src[0].visual_dump_final()
            >>> states['C1']['State']['value'], states['C3']['Acknowledge']['value']
            ('False', 'True')
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


@checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
@checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
def get_runs_from_application(application):
    runs = []
    origin_transitions = []
    application = type(application)()
    application.start(default_state_value=False)
    for _component in application.components.values():
        for _transition in _component.state_machine.transitions:
            if not len(_transition.incoming):
                origin_transitions.append(_transition)
    for _o in origin_transitions:
        sandbox = checkmate.sandbox.CollectionSandbox(application)
        for split, _t in sandbox(_o):
            runs.append(_t)
    return runs


def get_runs_from_itp(itp, application):
    runs = []
    application = type(application)()
    application.start()
    sandbox = checkmate.sandbox.CollectionSandbox(application, [itp])
    for split, _t in sandbox(itp, foreign_transitions=True):
        _t.itp_transition = itp
        runs.append(_t)
    return runs
