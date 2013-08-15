import os.path

import checkmate.component

import sample_app.exchanges
import sample_app.component_3.states

class Component_3(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_3.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

