import os
import yaml

import checkmate.application

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application,
                  metaclass=checkmate.application.ApplicationMeta):
    """"""
    itp_definition = ['pytango/checkmate']
    feature_definition_path = 'sample_app/itp'
    component_definition = 'pytango/checkmate/component'
    exchange_definition = ['pytango/checkmate/exchanges']
    test_data_definition = ['pytango/checkmate/test_data.yaml']
    data_structure_definition = ['pytango/checkmate/data_structures']

    c2_env = {'PATH': os.environ['PY2_VIRTUAL_ENV'] + '/bin:' +
                      os.environ['PATH'],
              'LD_LIBRARY_PATH': os.environ['BOOST_ROOT_PY2'] +
                                 '/lib:' + os.environ['LD_LIBRARY_PATH']}

    component_classes = yaml.load(
        """
        C1:
            - Component_1
            - launch_command: "python ./pytango/component/component_1.py
                                    {component.name}"
        C2:
            - Component_2
            - launch_command: python pytango/component/component_2_taurus.py
              command_env: %s
        C3:
            - Component_3
            - launch_command: ./pytango/component/Component_3 {component.name}
        USER:
            - User
            - {}
        """ % yaml.dump(c2_env))

    communication_list = {
        'pytango': pytango.checkmate.runtime.communication.Communication}

