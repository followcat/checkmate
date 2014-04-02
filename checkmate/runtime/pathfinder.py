import collections

import checkmate._tree
import checkmate.sandbox
import checkmate.transition
import checkmate.runtime.procedure


class TransitionTree(checkmate._tree.Tree):
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
            >>> tree = checkmate.runtime.pathfinder.TransitionTree(test_transition)
            >>> (tree.root.incoming[0].code, tree.root.outgoing[0].code, tree.root.outgoing[1].code)
            ('AC', 'RE', 'ARE')
            >>> tt = checkmate.runtime.pathfinder.TransitionTree(checkmate.test_data.App().components['C1'].state_machine.transitions[0])
            >>> tt.root #doctest: +ELLIPSIS
            <checkmate.transition.Transition object at ...
        """
        assert type(transition) == checkmate.transition.Transition
        super(TransitionTree, self).__init__(transition, [])

    def merge(self, tree):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> import checkmate.runtime.pathfinder
            >>> a = checkmate.test_data.App()
            >>> t1 = a.components['C1'].state_machine.transitions[0]
            >>> t2 = a.components['C3'].state_machine.transitions[0]
            >>> tree1 = checkmate.runtime.pathfinder.TransitionTree(t1)
            >>> tree2 = checkmate.runtime.pathfinder.TransitionTree(t2)
            >>> tree1.merge(tree2)
            True
            >>> len(tree1.nodes)
            1
            >>> tree1.nodes[0] == tree2
            True
        """
        is_merged = False
        if (not is_merged) and self.match_parent(tree):
            self.add_node(tree)
            is_merged = True
        else:
            for node in self.nodes:
                if node.merge(tree):
                    is_merged = True
        return is_merged

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

class RunCollection(list):
    def build_trees_from_application(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.runtime.pathfinder
            >>> runs = checkmate.runtime.pathfinder.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData)
            >>> len(runs)
            3
        """
        application = application_class()
        for _component in list(application.components.values()):
            for _transition in _component.state_machine.transitions:
                _tree = TransitionTree(_transition)
                self._add_tree(_tree)

    def _add_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> run = checkmate.runtime.pathfinder.RunCollection()
            >>> a = sample_app.application.TestData()
            >>> tree1 = checkmate.runtime.pathfinder.TransitionTree(a.components['C1'].state_machine.transitions[0])
            >>> tree2 = checkmate.runtime.pathfinder.TransitionTree(a.components['C3'].state_machine.transitions[0])
            >>> tree3 = checkmate.runtime.pathfinder.TransitionTree(a.components['C2'].state_machine.transitions[1])
            >>> (tree1.root.incoming[0].code, tree2.root.incoming[0].code, tree3.root.incoming[0].code)
            ('AC', 'RE', 'ARE')
            >>> run._add_tree(tree1)
            >>> run._add_tree(tree2)
            >>> run._add_tree(tree3)
            >>> len(run)
            1
            >>> tree2 in tree1.nodes, tree3 in tree1.nodes 
            (True, True)
        """
        is_merged = False
        for _tree in self:
            if _tree.merge(des_tree):
                is_merged = True
            if des_tree.merge(_tree):
                self.remove(_tree)
                self._add_tree(des_tree)
                is_merged = True
        if not is_merged and des_tree not in self:
            self.append(des_tree)

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
        proc = checkmate.runtime.procedure.Procedure(is_setup=True)
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
        >>> ac_run = [r for r in runs if r.root.outgoing[0].code == 'AC'][0]
        >>> rl_run = [r for r in runs if r.root.outgoing[0].code == 'RL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box([ac_run.root, rl_run.root])
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
        box([_run.root])
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
