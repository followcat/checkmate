# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
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
        - class: sample_app/component/user.yaml
          attributes: {}
          instances:
            - name: USER
        """)

    communication_list = {'': checkmate.runtime._pyzmq.Communication}


    def __init__(self):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']   
            >>> a.start()
            >>> c.states[0].value
            True
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-01', ...
            >>> ds = sample_app.data_structure.ActionRequest('HIGH') 
            >>> i = sample_app.exchanges.Action('AP')
            >>> c.process([i])[-1] # doctest: +ELLIPSIS
            <sample_app.exchanges.ThirdAction object at ...
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object ...
            >>> i = sample_app.exchanges.Action('AC')
            >>> t = c.engine.transitions[0]
            >>> t.is_matching_incoming([i], c.states)
            True
            >>> c.process([i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[0].value
            False
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-02', ...
            >>> result = c.process([i])
            >>> result # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> result[1].value
            False
            >>> c.states[0].value
            False
            >>> i = sample_app.exchanges.Action('PP')
            >>> t = c.engine.transitions[2]
            >>> t.is_matching_incoming([i], c.states)
            True
            >>> c.process([i])[-1] # doctest: +ELLIPSIS
            <sample_app.exchanges.Pause object at ...
            >>> c.states[1].value
            []

        """
        super(TestData, self).__init__()

