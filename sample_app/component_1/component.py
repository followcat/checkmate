# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os.path

import checkmate.component

import sample_app.exchanges
import sample_app.component_1.states

class Component_1(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_1.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

