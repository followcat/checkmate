# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import yaml

import checkmate.application

import pytango.checkmate.runtime.communication


class FullPython(checkmate.application.Application,
                 metaclass=checkmate.application.ApplicationMeta):
    """
        >>> import pytango.checkmate.application
        >>> import time
        >>> import pytango.checkmate.exchanges
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> ac = pytango.checkmate.python_application.FullPython
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> threaded = True
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded)
        >>> r.setup_environment(['C3'])
        >>> time.sleep(1)
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> simulated_transition =
        ...     c2.context.get_blocks_by_output(
        ...         [pytango.checkmate.exchanges.AC()])
        >>> o = c2.simulate(simulated_transition)
        >>> time.sleep(1)
        >>> _t = c1.context.engine.blocks[0]
        >>> _t.is_matching_incoming(o)
        >>> c1.validate(_t)
        True
        >>> r.stop_test()

    """
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
              launch_command: "python ./pytango/component/component_2.py
                                  {component.name}"
            instances:
              - name: C2
          - class: pytango/checkmate/component/component_3.yaml
            attributes:
              launch_command: "python ./pytango/component/component_3.py
                                  {component.name}"
            instances:
              - name: C3
        """)

    communication_list = {
        'pytango': pytango.checkmate.runtime.communication.Communication}

