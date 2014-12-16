import zope.interface

import checkmate._tree
import checkmate.sandbox
import checkmate.transition
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IRun)
class Run(checkmate._tree.Tree):
    def __init__(self, transition, nodes=None):
        assert type(transition) == checkmate.transition.Transition
        if nodes is None:
            nodes = []
        super(Run, self).__init__(transition, nodes)


class RunCollection(list):
    def get_origin_transition(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.RunCollection()
            >>> src.get_runs_from_application(sample_app.application.TestData())
            >>> [_t.outgoing[0].code for _t in src.origin_transitions]
            ['PBAC', 'PBRL', 'PBPP']
        """
        origin_transitions = []
        for _component in self.application.components.values():
            for _transition in _component.state_machine.transitions:
                if not len(_transition.incoming):
                    origin_transitions.append(_transition)
        return origin_transitions

    @checkmate.report_issue('checkmate/issues/match_R2_in_runs.rst', failed=1)
    @checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
    def get_runs_from_application(self, application):
        self.clear()
        self.application = type(application)()
        self.application.start(default_state_value=False)
        self.origin_transitions = self.get_origin_transition()
        for _o in self.origin_transitions:
            sandbox = checkmate.sandbox.CollectionSandbox(self.application)
            for split, _t in sandbox(_o):
                self.append(_t)
