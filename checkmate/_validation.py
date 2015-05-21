# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections


class ValidationDict(object):
    def __init__(self):
        super().__init__()
        self.collected_items = list()
        self.validated_items = list()

    def record(self, item_list):
        self.collected_items.append(item_list)
        self.validated_items.append(item_list)

    def check(self, items):
        try:
            self.collected_items.remove(items)
            return True
        except ValueError:
            return False

    def clear(self):
        self.collected_items.clear()
        self.validated_items.clear()
