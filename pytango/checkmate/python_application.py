import checkmate.application

import pytango.checkmate.runtime.communication


class FullPython(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    """
        >>> import pytango.checkmate.application
        >>> import time
        >>> import pytango.checkmate.exchanges
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> ac = pytango.checkmate.python_application.FullPython
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded=True)
        >>> r.setup_environment(['C3'])
        >>> time.sleep(1)
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> simulated_transition = c2.context.get_transition_by_output([pytango.checkmate.exchanges.AC()])
        >>> o = c2.simulate(simulated_transition)
        >>> time.sleep(1)
        >>> c1.context.state_machine.transitions[0].is_matching_incoming(o)
        >>> c1.validate(c1.context.state_machine.transitions[0])
        True
        >>> r.stop_test()

    """
    feature_definition_path = 'sample_app/itp'
    data_structure_definition = 'pytango/checkmate/data_structures'
    exchange_definition = 'pytango/checkmate/exchanges'
    test_data_definition = 'pytango/checkmate/test_data.yaml'

    component_classes = {('C1',): ('Component_1', {'launch_command': "python ./pytango/component/component_1.py {component.name}"}),
                         ('C2',): ('Component_2', {'launch_command': "python ./pytango/component/component_2.py {component.name}"}),
                         ('C3',): ('Component_3', {'launch_command': "python ./pytango/component/component_3.py {component.name}"}),
                         ('USER',): ('User', {}),
                        }
    communication_list = (pytango.checkmate.runtime.communication.Communication,)

