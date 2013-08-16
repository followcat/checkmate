import collections
import docutils.core
import docutils.nodes

import checkmate.state

from checkmate.parser.exceptions import *

class Writer(docutils.writers.Writer):
  
    def __init__(self, document, declarator):
        super(Writer, self).__init__()
        self.translator_class = DocTreeVisitor
        self.document = document
        self.declarator = declarator

    def translate(self):
        self.visitor = self.translator_class(self.document, self.declarator)
        self.document.walkabout(self.visitor)


class DocTreeVisitor(docutils.nodes.GenericNodeVisitor):
    """this visitor is visit table in restructure text

        >>> import checkmate.partition_declarator
        >>> import sample_app.exchanges
        >>> import sample_app.data_structure
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> import docutils.core
        >>> dt = docutils.core.publish_doctree(source=c)
        >>> declarator = checkmate.partition_declarator.Declarator(sample_app.data_structure, exchange_module=sample_app.exchanges)
        >>> wt = Writer(dt, declarator)
        >>> wt.translate() 
        >>> wt.visitor._state_partitions
        []
        >>> wt.visitor._data_structure_partitions # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.data_structure.IAttribute>, <checkmate._storage.PartitionStorage object at ...
        >>> wt.visitor._exchange_partitions # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.exchanges.IAction>, <checkmate._storage.PartitionStorage object at ...
        >>> len(wt.visitor._exchange_partitions)
        2
        >>> wt.visitor._transitions
        []
    """

    def __init__(self, document, declarator):
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.document = document
        self.declarator = declarator

    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_document(self, node):
        self._state_partitions = []
        self._data_structure_partitions = []
        self._exchange_partitions = []
        self._transitions = []
        self.inside_system_message = False
        self._high_level_flag = [0, 0, 0]
        self._low_level_flag = [0, 0, 0]
        self.codes = []
        self.full_description = collections.OrderedDict()
        self.standard_methods = {}
        self._state_keys = ''
        self._classname = '' 
        self.tran_titles = []
        self.array_items = []
        self.inside_table = False
        self.inside_tbody = False
        self.inside_thead = False
        self.title_level = 1

    def depart_document(self, node):
        pass

    def visit_section(self, node):
        self.title_level += 1

    def depart_section(self, node):
        if self.title_level == 4:
            #hardcode the module 
            if self._high_level_flag == [1, 0, 0]:
                assert (len(self._classname) != 0), "state class name empty"
                self._state_partitions.append(self.get_partitions('states'))
            elif self._high_level_flag == [0, 1, 1]:
                assert (len(self._classname) != 0), "data structure class name empty"
                self._data_structure_partitions.append(self.get_partitions('data_structure'))
            elif self._high_level_flag == [0, 1, 0]:
                assert (len(self._classname) != 0), "exchange class name empty"
                self._exchange_partitions.append(self.get_partitions('exchanges'))
            elif self._high_level_flag == [0, 0, 1]:
                assert (len(self.array_items) != 0), "transition empty"
                self._transitions += self.get_transition(self.array_items, self.tran_titles)
            self.full_description = collections.OrderedDict()
            self.standard_methods = {}
            self.codes = []
            self._classname = ''
            self.array_items = []
            self.tran_titles = []
        self.title_level -= 1

    def visit_title(self, node):
        if self.inside_system_message:
            return

        title = node.astext()
        #restore the key of simplestate
        if self._high_level_flag == [1, 0, 0] and self.title_level == 4:
            self._state_keys = title
        #flag the high section
        if title == 'State identification':
            self._high_level_flag = [1, 0, 0]
        elif title == 'Exchange identification':
            self._high_level_flag = [0, 1, 0]
        elif title == 'State machine': 
            self._high_level_flag = [0, 0, 1]
        elif title == 'Data structure':
            self._high_level_flag = [0, 1, 1]
        #flag the low section
        if title == 'Definition and accessibility' or title == 'Definition':
            assert self.title_level == 5, "source file is not in good format"
            self._low_level_flag = [1, 0, 0]
        elif  title == 'Value partitions':
            assert self.title_level == 5, "source file is not in good format"
            self._low_level_flag = [0, 1, 0]
        elif  title == 'Standard methods' or title == 'Exchange' or title == 'Transitions - exchanges':
            assert self.title_level == 5, "source file is not in good format"
            self._low_level_flag = [0, 0, 1]
 
    def depart_title(self, node):
        pass

    def visit_table(self, node):
        self.inside_table = True

    def depart_table(self, node):
        self.inside_table = False

    def visit_tbody(self, node):
        self.inside_tbody = True

    def depart_tbody(self, node):
        self.inside_tbody = False

    def visit_thead(self, node):
        self.inside_thead = True

    def depart_thead(self, node):
        self.inside_thead= False

    def visit_row(self, node):
        if self.inside_thead == True:
            self.tran_titles.extend(node.astext().split('\n\n'))
        if self.inside_tbody == False:
            return
        row = node.astext()
        content = row.split('\n\n')
        if self._high_level_flag == [1, 0, 0] :
            if  self._low_level_flag == [0, 1, 0]:
                assert (len(content) == 4), "4 columns are expected in state value partitions table row"
                id = content[0]
                code = content[1]
                val = content[2]
                com = content[3]
                self.codes.append(code)
                self.full_description[code] = (id, val, com)
            elif self._low_level_flag == [0, 0, 1]:
                assert (len(content) == 2), "2 columns are expected in State standard method table row"
                code = content[0]
                com = content[1]
                # Add standard member function to class
                try:
                    self.standard_methods[code] = getattr(checkmate.state, code)
                except AttributeError:
                    raise AttributeError(checkmate.state.__name__+' has no method defined: '+code)
        elif self._high_level_flag == [0, 1, 0] and self._low_level_flag == [0, 1, 0]:
            assert (len(content) == 4), "4 columns are expected in Exchange value partitions table row"
            id = content[0]
            code = content[1]
            val = content[2]
            com = content[3]
            self.codes.append(code)
            self.full_description[code] = (id, val, com)
        elif self._high_level_flag == [0, 0, 1] and self._low_level_flag == [0, 0, 1]:
            self.array_items.append(content)
        elif self._high_level_flag == [0, 1, 1] and self._low_level_flag == [0, 1, 0]:
            assert (len(content) == 4), "4 columns are expected in Data structure value partitions table row"
            id = content[0]
            code = content[1]
            val = content[2]
            com = content[3]
            self.codes.append(code)
            self.full_description[code] = (id, val, com)

    def depart_row(self, node):
        pass

    def visit_entry(self, node):
        entry = node.astext()

    def depart_entry(self, node):
        pass

    def visit_system_message(self, node):
        self.inside_system_message = True

    def depart_system_message(self, node):
        self.inside_system_message = False

    def visit_paragraph(self, node):
        if self.inside_table or self.inside_system_message:
            return
        paragraph = node.astext()
        if self._low_level_flag == [1, 0, 0]:
            texts = paragraph.split('\n')
            self._classname = str(texts[0])
             
    def get_partitions(self, partition_type):
        (interface, partition_storage) =  self.declarator.new_partition(partition_type, self._classname, self.standard_methods, self.codes, self.full_description)
        return (interface, partition_storage)

    def get_transition(self, array_items, tran_titles):
        component_transition =  self.declarator.new_transition(array_items, tran_titles)
        return component_transition


def call_visitor(content, declarator):
    """

        >>> import checkmate.partition_declarator
        >>> import sample_app.exchanges
        >>> import sample_app.data_structure
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> declarator = checkmate.partition_declarator.Declarator(sample_app.data_structure, exchange_module=sample_app.exchanges)
        >>> output = call_visitor(c, declarator)
        >>> output['data_structure'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.data_structure.IAttribute>, <checkmate._storage.PartitionStorage object at ...
        >>> len(output['data_structure'])
        3
        >>> output['exchanges'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.exchanges.IAction>, <checkmate._storage.PartitionStorage object at ...
        >>> len(output['exchanges'])
        2
        >>> import sample_app.component_1.states
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/component_1/state_machine.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> declarator = checkmate.partition_declarator.Declarator(sample_app.data_structure, state_module=sample_app.component_1.states, exchange_module=sample_app.exchanges)
        >>> output = call_visitor(c, declarator)
        >>> output['states'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.component_1.states.IState>, <checkmate._storage.PartitionStorage object at ...
        >>> len(output['states'])
        2
    """
    dt = docutils.core.publish_doctree(source=content)
    wt = Writer(dt, declarator)
    wt.translate()
    return {'states': wt.visitor._state_partitions,
            'data_structure': wt.visitor._data_structure_partitions,
            'exchanges': wt.visitor._exchange_partitions,
            'transitions': wt.visitor._transitions}
    
def main():
    input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst'
    f1 = open(input_file)
    content = f1.read()
    f1.close()
    visitor_output = call_visitor(content)
    component_state = visitor_output['states']
    component_exchange = visitor_output['exchanges']
    component_transitions = visitor_output['transitions']
    print('c_state: ')
    print(component_state)
    print('c_exchanges: ')
    print(component_exchange)
    print('c_transitions: ')
    print(component_transitions)

if __name__ == '__main__':
    main()

