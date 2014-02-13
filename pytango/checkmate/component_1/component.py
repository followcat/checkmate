import checkmate.component

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_1.states

import pytango.checkmate.runtime.communication_1


class Component_1(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_1.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication_1.Connector,)

    def __init__(self, name, full_python=False):
        super(Component_1, self).__init__(name, full_python)
        if full_python:
            self.launch_command = "python ./pytango/component_1/component.py {component.name}"
        else:
            self.launch_command = "java -classpath {classpath}:. pytango.jclient.component_1.Component {component.name}"

