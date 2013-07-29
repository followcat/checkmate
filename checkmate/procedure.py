import collections

import checkmate.parser.doctree


class Procedure(object):
    """"""
    def __init__(self, name, path, _class, history=[], setup_procedure='-', teardown_procedure='-', initial_state=[], final_state=[], exchanges=[]):
        """"""
        self.name = name
        self.path = path
        self._class = _class
        self.history = history
        self.setup_procedure = setup_procedure
        self.teardown_procedure = teardown_procedure
        self.initial_state = initial_state
        self.final_state = final_state
        self.exchanges = exchanges

    def tsv(self):
        """
            >>> name = "Procedure"
            >>> path = "/home/vcr/Projects/Checkmate/test_procedures.py"
            >>> _class = "TestProcedure"
            >>> p = Procedure(name, path, _class)
            >>> p.history = ['ALL']
            >>> p.setup_procedure = 'TestSetup'
            >>> p.teardown_procedure = 'TestTeardown'
            >>> p.initial_state = ['Q0()', 'M0(AUTO)', 'R0(0)']
            >>> p.final_state = ['Q0()', 'M0(MANUAL)', 'R0(0)']
            >>> p.exchanges = [['TM()', 'mcrhci', 'abs', 'HCI toggle request'], ['ST()', 'abs', 'mcrhci', 'Beam scheduler publish state']]
            >>> p.tsv() # doctest: +SKIP
        """
        buffer = "Procedure identification\n"
        buffer += self.name + '\n'
        buffer += 'Implementation\n{table heading_lines 0}\n'
        buffer += 'path\t' + self.path + '\n'
        buffer += 'class\t' + self._class + '\n'
        buffer += 'Setup procedure\t' + self.setup_procedure + '\n'
        buffer += 'Teardown procedure\t' + self.teardown_procedure + '\n'
        buffer += '\nInitial state\n{table heading_lines 0}\n'
        buffer += '\n'.join(['Any of the states\t'+s for s in self.initial_state]) + '\n'
        buffer += '\nFinal state\n{table heading_lines 0}\n'
        buffer += '\n'.join(['Any of the states\t'+s for s in self.final_state]) + '\n'
        buffer += '\nTest partition\n'
        buffer += '\t'.join(['Info exchange', 'Origin', 'Destination', 'Comment']) + '\n'
        for exchange in self.exchanges:
            buffer += '\t'.join(exchange) + '\n'
        buffer += '\n\n\n'
        return buffer
    
    def doctree(self):
        """
            >>> name = "Procedure"
            >>> path = "/home/vcr/Projects/Checkmate/test_procedures.py"
            >>> _class = "TestProcedure"
            >>> p = Procedure(name, path, _class)
            >>> p.history = ['ALL']
            >>> p.setup_procedure = 'TestSetup'
            >>> p.teardown_procedure = 'TestTeardown'
            >>> p.initial_state = ['Q0()', 'M0(AUTO)', 'R0(0)']
            >>> p.final_state = ['Q0()', 'M0(MANUAL)', 'R0(0)']
            >>> p.exchanges = [['TM()', 'mcrhci', 'abs', 'HCI toggle request'], ['ST()', 'abs', 'mcrhci', 'Beam scheduler publish state']]
            >>> p.doctree() # doctest: +SKIP
        """
        buffer = collections.OrderedDict()
        implementation = ([], [])
        implementation[-1].append(['path', self.path])
        implementation[-1].append(['class', self._class])
        implementation[-1].append(['Setup procedure', self.setup_procedure])
        implementation[-1].append(['Teardown procedure', self.teardown_procedure])
        initial_state = ([], [['Any of the states', s] for s in self.initial_state])
        final_state = ([], [['Any of the states', s] for s in self.final_state])
        test_partitions = (['Info exchange', 'Origin', 'Destination', 'Comment'], self.exchanges)

        procedure = collections.OrderedDict()
        procedure[self.name] = collections.OrderedDict([('Implementation', implementation),
                                ('Initial state', initial_state),
                                ('Final state', final_state),
                                ('Test partition', test_partitions)])

        buffer['Procedure identification'] = procedure
        dt = checkmate.parser.doctree.get_document(buffer)
        return dt

