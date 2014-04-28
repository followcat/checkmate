import checkmate.component

import sample_app.exchanges
import sample_app.data_structure

import pytango.checkmate.runtime.communication

        
class Component_3(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication.Connector,)

    def __init__(self, name, full_python=False):
        super(Component_3, self).__init__(name, full_python)
        if full_python:
            self.launch_command = "python ./pytango/component/component_3.py {component.name}"
        else:
            self.launch_command = "./pytango/component/Component_3 {component.name}"
