import copy

import checkmate.run


class StateMachine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

