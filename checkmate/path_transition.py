import zope.interface

import checkmate.transition

class Path_Transition(object):
    """ this in new class to store the 'transitions' from exchange lists
    """
    def __init__(self, **argc):
        checkmate.transition.Transition.__init__(self, **argc)
        self.previous_transitions = [] 
        self.next_transitions = []

    def is_matching_initial(self, state_list):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> import copy
            >>> states = copy.deepcopy(a.components['C1'].states + a.components['C2'].states + a.components['C3'].states)
            >>> ex = sample_app.exchanges.AC()
            >>> pt = checkmate.path_transition.Path_Transition(initial=states, incoming=[ex], final=[], outgoing=[])
            >>> a.components['C1'].states[0].value
            'True'
            >>> pt.is_matching_initial(a.components['C1'].states)
            True
            >>> output = a.components['C1'].process([ex])
            >>> a.components['C1'].states[0].value
            'False'
            >>> pt.is_matching_initial(a.components['C1'].states)
            False
        """
        return compare_state(self.initial, state_list)

    def is_matching_final(self, state_list):
        return compare_state(self.final, state_list)


def compare_state(states, target):
    if len(states) == 0 or len(target) == 0: 
        return True
    matching = 0
    for _k in target:
        _interface = zope.interface.implementedBy(_k.__class__)
        try:
            _state = [_s for _s in states if _interface.providedBy(_s)].pop(0)
            if _state == _k:
                matching += 1
            else:
                break
        except IndexError:
            continue
    # Do not check len(local_copy) as some state_list are not in self.initial
    return matching == len(target)

        
