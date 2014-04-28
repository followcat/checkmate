import os.path

import checkmate.component
import checkmate.runtime._pyzmq

import sample_app.exchanges

        
class Component_2(checkmate.component.Component, metaclass=checkmate.component.ComponentMeta):
    """"""
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges
    connector_list = (checkmate.runtime._pyzmq.Connector,)

