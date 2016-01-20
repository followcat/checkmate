# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import yaml

import checkmate.application

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application,
                  metaclass=checkmate.application.ApplicationMeta):
    """
        >>> import pytango.checkmate.application
        >>> a = pytango.checkmate.application.Application()
        >>> c1 = a.components['C1']
        >>> c1.engine.blocks[-1].outgoing[0].code
        'PA'
    """
    c2_env = {'PATH': os.environ['PY2_VIRTUAL_ENV'] + '/bin:' +
                      os.environ['PATH'],
              'LD_LIBRARY_PATH': os.environ['BOOST_ROOT_PY2'] +
                                 '/lib:' + os.environ['LD_LIBRARY_PATH']}

    application_definition = yaml.load(
        """
        itp_definition: pytango/checkmate
        feature_definition_path: sample_app/itp
        exchange_definition: pytango/checkmate/exchanges
        test_data_definition: pytango/checkmate/test_data.yaml
        data_structure_definition: pytango/checkmate/data_structures
        component_classes:
          - class: pytango/checkmate/component/component_1.yaml
            attributes:
              launch_command: "python ./pytango/component/component_1.py
                                  {component.name}"
            instances:
              - name: C1
          - class: pytango/checkmate/component/component_2.yaml
            attributes:
              launch_command: python pytango/component/component_2_taurus.py
              command_env: %s
            instances:
              - name: C2
          - class: pytango/checkmate/component/component_3.yaml
            attributes:
              launch_command: ./pytango/component/Component_3 {component.name}
            instances:
              - name: C3
        """ % yaml.dump(c2_env))

    communication_list = {
        'pytango': pytango.checkmate.runtime.communication.Communication}

