import zope.interface

import checkmate._tree
import checkmate.sandbox
import checkmate.transition
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IRun)
class Run(checkmate._tree.Tree):
    def __init__(self, transition, nodes=None, states=None):
        assert type(transition) == checkmate.transition.Transition
        if nodes is None:
            nodes = []
        if states is None:
            states = []
        super(Run, self).__init__(transition, nodes)
        self.change_states = []
        for f in transition.final:
            for s in states:
                if f.interface.providedBy(s):
                    self.change_states.append((type(s).__name__, s._dump()))
                    break

    def __call__(self):
        pass

    def visual_dump(self):
        dump_dict = {}
        dump_dict['root'] = self.root.name
        dump_dict['owner'] = self.root.owner
        dump_dict['incoming'] = [i.origin_code for i in self.root.incoming]
        dump_dict['outgoing'] = [o.origin_code for o in self.root.outgoing]
        dump_dict['states'] = dict(self.change_states)
        dump_dict['nodes'] = []
        for element in self.nodes:
            dump_dict['nodes'].append(element.visual_dump())
        return dump_dict

    def visual_states(self, states, owner="", level=0):
        tab_space = ' ' * 6 * level
        return_str = ""
        for state, values in states.items():
            state_str = """
{space}      {owner}: {state} - {value}""".format(space=tab_space, owner=owner, state=state, value=values['value'])
            return_str += state_str
            attr_space_len = len(state_str) - len(values['value'].__str__())
            for name, value in values.items():
                if name != 'value':
                    return_str += """
{space}{name}: {value}""".format(space=' ' * attr_space_len, name=name, value=value)
        return return_str

    def visual_run(self, level=0):
        visual_dump = self.visual_dump()
        tab_space = ' ' * 6 * level

        owner = visual_dump['owner']
        final_states = self.visual_states(visual_dump['states'], owner, level)
        string = """
{space}|
{space}|     +-----------------------+
{space}|     | {incoming}
{space}|_____|
{space}      | {outgoing}
{space}      +-----------------------+{final}
        """.format(space=tab_space, incoming=visual_dump['incoming'], outgoing=visual_dump['outgoing'], final=final_states)
        for element in self.nodes:
            string += element.visual_run(level + 1)
        return string

    def initial_states(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.RunCollection()
            >>> src.get_runs_from_application(sample_app.application.TestData())
            >>> states = src[0].initial_states()
            >>> states['State']['value'], states['Acknowledge']['value']
            ('True', 'False')
        """
        state_dict = {}
        for run in self.breadthWalk():
            for _s in run.root.initial:
                state = _s.factory()
                cls_name = type(state).__name__
                if cls_name not in state_dict:
                    state_dict[cls_name] = state._dump()
        return state_dict

    def final_states(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.RunCollection()
            >>> src.get_runs_from_application(sample_app.application.TestData())
            >>> states = src[0].final_states()
            >>> states['State']['value'], states['Acknowledge']['value']
            ('False', 'True')
        """
        state_dict = {}
        for run in self.breadthWalk():
            for state in run.change_states:
                state_dict[state[0]] = state[1]
        return state_dict


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
