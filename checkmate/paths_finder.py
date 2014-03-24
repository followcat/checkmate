import checkmate._newtree
import checkmate.run_transition


class HumanInterfaceExchangesFinder(object):
    def __init__(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> hi = checkmate.paths_finder.HumanInterfaceExchangesFinder(sample_app.application.TestData)
            >>> hi.human_interface_exchange_code_list
            ['AC', 'RL', 'PP']
        """
        self.transition_list = []
        self.human_interface_exchange_code_list = []
        self.application = application_class()
        self.get_Importent_Exchange_from_application()

    def get_Importent_Exchange_from_application(self):
        for _k, _v in self.application.components.items():
            self.transition_list.extend(_v.state_machine.transitions)
        for _t in self.transition_list:
            if len(_t.incoming) == 0 and len(_t.outgoing) > 0:
                for _outgoing in _t.outgoing:
                    self.human_interface_exchange_code_list.append(_outgoing.code)

class PathBuilder(object):
    def __init__(self, application_class):
        self.path_list = []
        self.application_class = application_class
        self.tree_list = checkmate.runtime.pathfinder.RunCollection()
        self.tree_list.build_trees_from_application(application_class)

    def make_path(self, unprocessed = None, unprocessed_initial_state = None):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> pb = checkmate.paths_finder.PathBuilder(sample_app.application.TestData)
        """
        if unprocessed is None:
            unprocessed = self.tree_list
        found = False
        for _i, _unprocessed in enumerate(unprocessed):
            found = False
            process_exchange_list = [_unprocessed[_node].tag for _node in _unprocessed.expand_tree(mode=checkmate._newtree.NewTree.ZIGZAG)]
            temp_transition = checkmate.run_transition.get_transition(self.application_class,process_exchange_list, unprocessed_initial_state[_i])
            if temp_transition is not None:
                self.path_list.append([temp_transition])
                found = True
            else:
                for _path in self.path_list:
                    if len(unprocessed) <= 0:
                        break
                    temp_transition = checkmate.run_transition.get_transition(self.application_class, process_exchange_list, _unprocessed, _path)
                    if temp_transition is not None:
                        new_path = _path[0:_path.index(temp_transition.previous_transitions[0])+1]
                        new_path.append(temp_transition)
                        #replace the current path with newer longer one
                        if len(new_path) > len(_path):
                            self.path_list.remove(_path)
                        self.path_list.append(new_path)
                        found = True
                for _p in self.path_list:
                    for _s in _p:
                        if _s.is_matching_final(temp_transition.initial) and temp_transition not in _s.previous_transitions:
                            _s.next_transitions.append(temp_transition)
                        if _s.is_matching_initial(temp_transition.final) and temp_transition not in _s.next_transitions:
                            _s.previous_transitions.append(temp_transition)
            if found:
                unprocessed.remove(_u)
                self.make_path(unprocessed, unprocessed_initial_state)
                break 
