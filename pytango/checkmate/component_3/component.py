import checkmate.component

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_3.states

import pytango.checkmate.runtime.communication_3

        
class Component_3(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    state_module = sample_app.component_3.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication_3.Connector,)

