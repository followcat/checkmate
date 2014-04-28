import os.path

import checkmate.application
import checkmate.runtime._pyzmq

import sample_app.exchanges
import sample_app.data_structure

class TestData(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    """"""
    __test__ = False

    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

    def __init__(self, full_python=False):
        """
            >>> import sample_app.application
            >>> import checkmate.component
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']   
            >>> a.start()
            >>> c.states[0].value
            'True'
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-01', ...
            >>> ds = sample_app.data_structure.Attribute('AT2') 
            >>> ds.description() # doctest: +ELLIPSIS
            ('D-ATTR-02', ...
            >>> i = sample_app.exchanges.AP()
            >>> c.process([i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.ThirdAction object at ...
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> i = sample_app.exchanges.AC()
            >>> t = c.state_machine.transitions[0]
            >>> t.is_matching_incoming([i])
            True
            >>> c.process([i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[0].value
            'False'
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-02', ...
            >>> c.process([i])
            []
            >>> c.states[0].value
            'False'
            >>> i = sample_app.exchanges.PP()
            >>> t = c.state_machine.transitions[2]
            >>> t.is_matching_incoming([i])
            True
            >>> c.process([i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Pause object at ...
            >>> c.states[1].value
            []

        """
        super(TestData, self).__init__(full_python)

        #can only be loaded after application exchanges.yaml is parsed by metaclass
        import sample_app.component.component_1
        import sample_app.component.component_2
        import sample_app.component.component_3

        self.components = {'C1': sample_app.component.component_1.Component_1,
                           'C2': sample_app.component.component_2.Component_2,
                           'C3': sample_app.component.component_3.Component_3}
        for name in list(self.components.keys()):
            self.components[name] = self.components[name](name)

        self.communication_list = (checkmate.runtime._pyzmq.Communication,)

