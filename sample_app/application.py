import os.path

import checkmate.application
import checkmate.parser.doctree

import sample_app.exchanges
import sample_app.component_1.component
import sample_app.component_2.component


class TestData(checkmate.application.Application):
    def __init__(self):
        """
            >>> import checkmate.component
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']   
            >>> a.start()
            >>> a.test_plan(['C1']) # doctest: +ELLIPSIS
            ((('C2', []), ('C1', [('True', 'S-STATE-01'), ([], 'S-ANOST-01')])), ('C2', [('AC', 'X-ACTION-01')]), (('C2', []), ('C1', [('False', 'S-STATE-02'), ([], 'S-ANOST-01')])), ('C1', [('RE', 'X-REACTION-01')]))
            ((('C2', []), ('C1', [('True', 'S-STATE-01'), (['R'], 'S-ANOST-02')])), ...
            >>> c.states[0].value
            'True'
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-01', ...
            >>> i = sample_app.exchanges.AP(R=1)
            >>> checkmate.component.execute(c, i) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[1].value
            [1]
            >>> i = sample_app.exchanges.AC()
            >>> t = c.state_machine.transitions[0]
            >>> t.is_matching_incoming(i)
            True
            >>> checkmate.component.execute(c, i) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[0].value
            'False'
            >>> c.states[0].description() # doctest: +ELLIPSIS
            ('S-STATE-02', ...
            >>> checkmate.component.execute(c, i)
            >>> c.states[0].value
            'False'
            >>> i = sample_app.exchanges.PP()
            >>> t = c.state_machine.transitions[2]
            >>> t.is_matching_incoming(i)
            True
            >>> checkmate.component.execute(c, i) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[1].value
            []

        """
        exchange_module = sample_app.exchanges
        path = os.path.dirname(exchange_module.__file__)
        filename = 'exchanges.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        super(TestData, self).__init__(matrix, exchange_module)

        self.components = {'C1': sample_app.component_1.component.Component_1,
                           'C2': sample_app.component_2.component.Component_2}
        for name in list(self.components.keys()):
            self.components[name] = self.components[name](name)

