import checkmate.application

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    exchange_definition_file = 'sample_app/exchanges.yaml'

    component_classes = {('C1',): ('Component_1', {'launch_command': "java -classpath {classpath}:. pytango.component.Component_1 {component.name}"}),
                         ('C2',): ('Component_2', {'launch_command': "./pytango/component/component_2"}),
                         ('C3',): ('Component_3', {'launch_command': "./pytango/component/Component_3 {component.name}"}),
                         ('USER',): ('User', {}),
                        }

    communication_list = (pytango.checkmate.runtime.communication.Communication,)

