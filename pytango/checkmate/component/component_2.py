import checkmate.component

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_2.states

import pytango.checkmate.runtime.communication

        
class Component_2(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    state_module = sample_app.component_2.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication.Connector,)
    launch_command = "python ./pytango/component/component_2.py {component.name}"

