# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.


class Engine(object):
    def __init__(self, states=[], transitions=[]):
        self.states = states
        self.transitions = transitions

