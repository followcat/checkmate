
class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

    def transition_by_name(self, name):
        for _t in self.transitions:
            if _t.name == name:
                return _t

