import checkmate.application

import sample_app.exchanges

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    exchange_module = sample_app.exchanges

    component_classes = {('C1',): ('Component_1', {'launch_command': "java -classpath {classpath}:. pytango.component.Component_1 {component.name}"}),
                         ('C2',): ('Component_2', {}),
                         ('C3',): ('Component_3', {'launch_command': "./pytango/component/Component_3 {component.name}"}),
                        }
    communication_list = (pytango.checkmate.runtime.communication.Communication,)

