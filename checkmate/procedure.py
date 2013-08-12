import collections

import checkmate.parser.doctree


class Procedure(object):
    """"""
    def __init__(self, index, stub_name, sut_name, sut_run):
        """"""
        self.index = index
        self.stub = stub_name
        self.sut = sut_name
        self.run = sut_run
        

    def _format_output(self):
        self.name = 'TestProcedure_{index}'.format(index=self.index)
        self.path = 'integration/procedures/test_{sut}.py'.format(sut=sut)
        self._class = 'Test{sut}{state}{incoming}'.format(sut=sut,state=''.join([i.partition_id for i in self.run.initial]), incoming = self.run.desc_incoming)
        self.history = ['Now']
        self.setup_procedure = '-'
        self.teardown_procedure = '-'
        self.initial_state = [s.partition_id for s in self.run.initial]
        self.final_state = [s.partition_id for s in self.run.final]

        exchanges = [[self.run.incoming.partition_id, self.run.incoming.origin, self.run.incoming.destination, self.run.desc_incoming]]
        for o in self.run.final:
            if (o.partition_id != self.run.initial[self.run.final.index(o)].partition_id):
                exchanges.append([o.partition_id, sut, sut, self.run.desc_final[self.run.final.index(o)]])
        for o in self.run.outgoing:
            exchanges.append([o.partition_id, sut, stub, self.run.desc_outgoing[self.run.outgoing.index(o)]])
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
        self._format_output()
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
        self._format_output()
        buffer = collections.OrderedDict()
        implementation = ([], [])
        implementation[-1].append(['path', self.path])
        implementation[-1].append(['class', self._class])
        implementation[-1].append(['Setup procedure', self.setup_procedure])
        implementation[-1].append(['Teardown procedure', self.teardown_procedure])
        if len(self.initial_state) == 0:
            self.initial_state = ['']
        initial_state = ([], [['Any of the states', s] for s in self.initial_state])
        if len(self.final_state) == 0:
            self.final_state = ['']
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

