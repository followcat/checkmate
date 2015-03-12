# This code is part of the checkmate project.
# Copyright (C) 2014 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

class List(list):
    def __init__(self, transitions):
        """
            >>> import checkmate._validation
            >>> import sample_app.application
            >>> app = sample_app.application.TestData()
            >>> c1 = app.components['C1']
            >>> l = checkmate._validation.List(c1.state_machine.transitions)
            >>> len(l)
            4
        """
        super().__init__(range(len(transitions)))
        self.transitions = transitions
        self.validated_items = []
        for index in range(len(transitions)):
            self[index] = []
            self.validated_items.append(list())

    def record(self, transition, item_list):
        """"""
        try:
            index = self.transitions.index(transition)
            for _item in item_list:
                self[index].append(_item)
                self.validated_items[index].append(_item)
        except ValueError:
            self.append(list())
            self.validated_items.append(list())
            self.transitions.append(transition)
            self.record(transition, item_list)

    def check(self, transition):
        """"""
        try:
            self[self.transitions.index(transition)].pop()
            return True
        except IndexError:
            return False
        except ValueError:
            return False

    def clear(self):
        """"""
        for index in range(len(self)):
            self[index] = []
            self.validated_items[index] = []

    def items(self, transition):
        """"""
        try:
            index = self.transitions.index(transition)
            return self.validated_items[index]
        except ValueError:
            return []

    def all_items(self):
        items = []
        for _i in self.validated_items:
            items += _i
        return items

