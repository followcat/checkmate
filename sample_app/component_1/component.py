import os.path

import checkmate.component

import sample_app.exchanges
import sample_app.component_1.states

class Component_1(checkmate.component.Component):
    def __init__(self):
        """
        """
        state_module = sample_app.component_1.states
        exchange_module = sample_app.exchanges
        path = os.path.dirname(state_module.__file__)
        filename = 'state_machine.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        super(Component_1, self).__init__(matrix, state_module, exchange_module)

        
