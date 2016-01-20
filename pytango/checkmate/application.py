# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os

import checkmate.application

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    feature_definition_path = 'sample_app/itp'
    exchange_definition_file = 'pytango/checkmate/exchanges.yaml'
    test_data_definition_file = 'pytango/checkmate/test_data.yaml'
    c2_env = {'PATH': os.environ['PY2_VIRTUAL_ENV'] + '/bin:' + os.environ['PATH'],
              'LD_LIBRARY_PATH': os.environ['BOOST_ROOT_PY2'] + '/lib:' + os.environ['LD_LIBRARY_PATH']}

    component_classes = {('C1',): ('Component_1', {'launch_command': "python ./pytango/component/component_1.py {component.name}"}),
                         ('C2',): ('Component_2', {'launch_command': "python pytango/component/component_2_taurus.py", 'command_env': c2_env}),
                         ('C3',): ('Component_3', {'launch_command': "./pytango/component/Component_3 {component.name}"}),
                         ('USER',): ('User', {}),
                        }

    communication_list = (pytango.checkmate.runtime.communication.Communication,)

