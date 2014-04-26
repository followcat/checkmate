import checkmate.component

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_1.states

import pytango.checkmate.runtime.communication


class Component_1(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_1.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication.Connector,)

    def __init__(self, name, full_python=False):
        super(Component_1, self).__init__(name, full_python)
        if full_python:
            self.launch_command = "python ./pytango/component/component_1.py {component.name}"
        else:
            self.launch_command = "java -classpath {classpath}:. pytango.component.Component_1 {component.name}"

