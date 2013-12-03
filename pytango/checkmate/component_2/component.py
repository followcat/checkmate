import checkmate.component
import checkmate.runtime._pyzmq

import sample_app.exchanges
import sample_app.data_structure
import sample_app.component_2.states

        
class Component_2(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    state_module = sample_app.component_2.states
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    communication_list = (checkmate.runtime._pyzmq.Communication,)

