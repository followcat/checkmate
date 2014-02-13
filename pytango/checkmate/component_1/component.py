import checkmate.component

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_1.states

import pytango.checkmate.runtime.communication_1


class Component(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    state_module = sample_app.component_1.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (pytango.checkmate.runtime.communication_1.Connector,)
    launch_command = "java -classpath {classpath}:. pytango.component_1.Component {component.name}"

