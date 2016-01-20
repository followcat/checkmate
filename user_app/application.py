# This code is part of the checkmate project.
# Copyright (C) 2015-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import yaml

import checkmate.application
import checkmate.runtime._pyzmq


class TestData(checkmate.application.Application,
               metaclass=checkmate.application.ApplicationMeta):
    """"""
    __test__ = False

    exchange_definition = 'sample_app/exchanges.yaml'
    test_data_definition = 'sample_app/test_data.yaml'

    component_classes = yaml.load(
        """
        - class: sample_app/component/component_3.yaml
          attributes: {}
          instances:
            - name: C3
        - class: sample_app/component/component_1.yaml
          attributes: {}
          instances:
            - name: C1
        - class: sample_app/component/component_2.yaml
          attributes: {}
          instances:
            - name: C2
              attributes:
                request:
                  C: AT1
                  P: NORM
        - class: user_app/component/user.yaml
          attributes: {}
          instances:
            - name: USER
        """)

    communication_list = {'': checkmate.runtime._pyzmq.Communication}


    @checkmate.fix_issue("user_app/issues/empty_user_collection.rst")
    def __init__(self):
        """
            >>> import user_app.application
            >>> import checkmate.parser.feature_visitor
            >>> a = user_app.application.TestData()
            >>> a.start()
            >>> state_modules = []
            >>> for name, component in a.components.items():
            ...     state_modules.append(component.state_module)
            >>> visitor = checkmate.parser.feature_visitor
            >>> data = visitor.data_from_files(a)
            >>> len(data)
            6
        """
        super(TestData, self).__init__()

