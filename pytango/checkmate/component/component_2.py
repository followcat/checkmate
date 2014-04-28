import checkmate.component

import sample_app.exchanges
import sample_app.data_structure

import pytango.checkmate.runtime.communication

        
class Component_2(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication.Connector,)
    launch_command = "python ./pytango/component/component_2.py {component.name}"

