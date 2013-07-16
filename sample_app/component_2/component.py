import os.path

import checkmate.component

import sample_app.exchanges
import sample_app.component_2.states

class Component_2(checkmate.component.Component):
    def __init__(self, name):
        """
        """
        state_module = sample_app.component_2.states
        exchange_module = sample_app.exchanges
        path = os.path.dirname(state_module.__file__)
        filename = 'state_machine.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        super(Component_2, self).__init__(name, matrix, state_module, exchange_module)

        
