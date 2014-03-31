import collections

import checkmate._tree
import checkmate.sandbox
import checkmate._newtree
import checkmate.transition
import checkmate.runtime.procedure


class TransitionTree(checkmate._newtree.NewTree):
    """"""
    def __init__(self, transition):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> import sample_app.data_structure
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'AC', None, sample_app.data_structure.ActionPriority)]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'RE', None, sample_app.data_structure.ActionPriority), checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'ARE', None, sample_app.data_structure.ActionPriority)]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list, outgoing = outgoing_list)
            >>> checkmate.runtime.pathfinder.TransitionTree(test_transition).showid()
            AC
            |___ ARE
            |___ RE
        """
        super().__init__()
        incoming_list = transition.incoming
        outgoing_list = transition.outgoing
        if incoming_list is None or len(incoming_list) == 0:
            _identifier = "~" + outgoing_list[0].code
        else:
            _identifier = incoming_list[0].code
        self.create_node(transition, _identifier)
        # add following transitions as children
        for _outgoing in outgoing_list:
            self.create_node(None, _outgoing.code, parent=_identifier)

class NewTransitionTree(checkmate._tree.Tree):
    """"""
    def __init__(self, transition):
        """
            >>> import checkmate.test_data
            >>> tt = checkmate.runtime.pathfinder.NewTransitionTree(checkmate.test_data.App().components['C1'].state_machine.transitions[0])
            >>> tt.root #doctest: +ELLIPSIS
            <checkmate.transition.Transition object at ...
        """
        assert type(transition) == checkmate.transition.Transition
        super(NewTransitionTree, self).__init__(transition)

    def merge(self, tree):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> t1 = a.components['C1'].state_machine.transitions[0]
            >>> t2 = a.components['C3'].state_machine.transitions[0]
            >>> t1.outgoing[0].code == t2.incoming[0].code
            True
            >>> tree1 = checkmate.runtime.pathfinder.NewTransitionTree(t1)
            >>> tree2 = checkmate.runtime.pathfinder.NewTransitionTree(t2)
            >>> tree1.match_parent(tree2)
            True
            >>> tree2.match_parent(tree1)
            False
            >>> tree2.merge(tree1)
            False
            >>> tree1.merge(tree2)
            True
        """
        if self.match_parent(tree):
            self.add_node(tree)
            return True
        for node in self.nodes:
            if node.merge(tree):
                return True
        return False

    def match_parent(self, tree):
        """
        """
        if len(self.root.outgoing) == 0 or len(tree.root.incoming) == 0:
            return False
        action_code = tree.root.incoming[0].code
        for _o in self.root.outgoing:
            if _o.code == action_code:
                return True
        return False

class NewRunCollection(list):
    def build_trees_from_application(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime.pathfinder
            >>> runs = checkmate.runtime.pathfinder.NewRunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData)
            >>> len(runs)
            3
        """
        application = application_class()
        for _component in list(application.components.values()):
            for _transition in _component.state_machine.transitions:
                _tree = NewTransitionTree(_transition)
                self._add_tree(_tree)

    def _add_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> r = checkmate.runtime.pathfinder.NewRunCollection()
            >>> a = sample_app.application.TestData()
            >>> tree1 = checkmate._tree.Tree(a.components['C1'].state_machine.transitions[0])
            >>> tree2 = checkmate._tree.Tree(a.components['C3'].state_machine.transitions[0])
            >>> tree3 = checkmate._tree.Tree(a.components['C2'].state_machine.transitions[1])
        """
        for _tree in self:
            if  _tree.merge(des_tree):
                return
            if des_tree.merge(_tree):
                self.remove(_tree)
                self.append(des_tree)
                return
        self.append(des_tree)

class RunCollection(list):
    def build_trees_from_application(self, application_class):
        """
            >>> import sample_app.application
            >>> runs = checkmate.runtime.pathfinder.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData)
            >>> len(runs)
            3
        """
        application = application_class()
        for _k, _v in application.components.items():
            for _t in _v.state_machine.transitions:
                temp_tree = TransitionTree(_t)
                if self.merge_tree(temp_tree) == False:
                    self.append(temp_tree)

    def merge_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> r = checkmate.runtime.pathfinder.RunCollection()
            >>> tree_one = checkmate._newtree.NewTree()
            >>> tree_one.create_node(sample_app.application.TestData().components['C1'].state_machine.transitions[0], 'AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_one.add_node(checkmate._newtree.NewNode(None, 'RE'), parent='AC')
            >>> tree_one.add_node(checkmate._newtree.NewNode(None, 'ARE'), parent='AC')
            >>> if r.merge_tree(tree_one) == False:
            ...        r.append(tree_one)
            >>> r[0].showid()
            AC
            |___ ARE
            |___ RE
            >>> tree_two = checkmate._newtree.NewTree()
            >>> tree_two.create_node(sample_app.application.TestData().components['C2'].state_machine.transitions[1], 'ARE') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_two.add_node(checkmate._newtree.NewNode(None, 'AP'), parent='ARE')
            >>> tree_two.showid()
            ARE
            |___ AP
            >>> r.merge_tree(tree_two)
            True
            >>> r[0].showid()
            AC
            |___ ARE
            |    |___ AP
            |___ RE
            >>> tree = r[0]
            >>> [tree.get_node(n)._tag for n in tree.get_node(tree.root).fpointer] # doctest: +ELLIPSIS
            [None, <checkmate.transition.Transition object at ...
        """
        found = False
        once_found = False
        for _tree in self[:]:
            found, des_tree = _tree.merge(des_tree)
            if found:
                once_found = True
                self.remove(_tree)
        if once_found:
            self.append(des_tree)
            self.merge_tree(des_tree)
        return once_found

def get_path_from_pathfinder(application, target):
    """
        >>> import zope.interface
        >>> import checkmate.sandbox
        >>> import checkmate.runtime.registry    
        >>> import checkmate.runtime.pathfinder
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> cc = checkmate.runtime.communication.Communication
        >>> _class = sample_app.application.TestData
        >>> runs = checkmate.runtime.pathfinder.RunCollection()
        >>> runs.build_trees_from_application(_class)
        >>> r = checkmate.runtime._runtime.Runtime(_class, cc)
        >>> box = checkmate.sandbox.Sandbox(_class())
        >>> ex1 = sample_app.exchanges.AC()
        >>> ex1.origin_destination('C2', 'C1')
        >>> exchanges = box.generate([ex1])
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> checkmate.runtime.registry.global_registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> generator = checkmate.runtime.pathfinder.get_path_from_pathfinder(app, proc.initial)
        >>> for setup in generator:
        ...     print(setup[0].exchanges.root.action, app.compare_states(setup[0].initial))
        RL True
        PP False
    """
    for _run, _app in _find_runs(application, target).items():
        proc = checkmate.runtime.procedure.Procedure()
        _app.fill_procedure(proc)
        yield (proc, )

def _find_runs(application, target):
    """
        >>> import checkmate.sandbox
        >>> import sample_app.application
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime.pathfinder
        >>> a = sample_app.application.TestData()
        >>> runs = checkmate.runtime.pathfinder.RunCollection()
        >>> runs.build_trees_from_application(type(a))
        >>> ac_run = [r for r in runs if r.get_node(r.root)._tag.outgoing[0].code == 'AC'][0]
        >>> rl_run = [r for r in runs if r.get_node(r.root)._tag.outgoing[0].code == 'RL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box([ac_run.get_node(ac_run.root)._tag, rl_run.get_node(rl_run.root)._tag,])
        True
        >>> proc = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator():
        ...     proc.append(p)
        ...     

        >>> nbox = checkmate.sandbox.Sandbox(box.application)
        >>> proc[0][0].exchanges.root.action
        'AC'
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[0][0].initial))
        1
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[2][0].initial))
        2
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[3][0].initial))
        3

    """
    runs = RunCollection()
    runs.build_trees_from_application(type(application))
    used_runs = _next_run(application, target, runs, collections.OrderedDict())
    return used_runs

def _next_run(application, target, runs, used_runs):
    box = checkmate.sandbox.Sandbox(application)
    for _run in runs:
        if _run in used_runs:
            continue
        box([_run.get_node(_run.root)._tag])
        if box.is_run:
            if box.application.compare_states(target):
                used_runs[_run] = box
                return used_runs
            else:
                used_runs.update({_run: box})
                returned_runs = _next_run(box.application, target, runs, used_runs)
                if len(returned_runs) == 0:
                    del used_runs[_run]
                    box = checkmate.sandbox.Sandbox(application)
                    continue
                else:
                    return returned_runs
    return collections.OrderedDict()
