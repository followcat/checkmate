import os.path

import checkmate.component

import sample_app.exchanges
import sample_app.component_1.states

class Component_1(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_1.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

