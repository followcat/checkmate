import copy
import functools
import collections
import docutils.core
import docutils.nodes

import zope.interface

import checkmate._utils
import checkmate.state
import checkmate.exchange
import checkmate.transition


def _to_interface(_classname):
    return 'I'+_classname

class Writer(docutils.writers.Writer):
  
    def __init__(self, document, state_module=None, exchange_module=None):
        docutils.writers.Writer.__init__(self)
        self.translator_class = DocTreeVisitor
        self.document = document
        self.state_module = state_module
        self.exchange_module = exchange_module
  
    def translate(self):
        self.visitor = visitor = self.translator_class(self.document, self.state_module, self.exchange_module)
        self.document.walkabout(visitor)
        #self.output = ''.join(visitor.output)

class DocTreeVisitor(docutils.nodes.GenericNodeVisitor):
    """this visitor is visit table in restructure text

        >>> import sample_app.exchanges
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> import docutils.core
        >>> dt = docutils.core.publish_doctree(source=c)
        >>> wt = Writer(dt, exchange_module=sample_app.exchanges)
        >>> wt.translate() 
        >>> wt.visitor._state_partitions
        []
        >>> wt.visitor._exchange_partitions # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.exchanges.IAction>, [<checkmate._storage.ExchangeStorage object at ...
        >>> len(wt.visitor._exchange_partitions)
        2
        >>> wt.visitor._transitions
        []
    """

    def __init__(self, document, state_module=None, exchange_module=None):
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.document = document
        self.state_module = state_module
        self.exchange_module = exchange_module

    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_document(self, node):
        self._state_partitions = []
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
        self.array_items = []
        self.inside_table = False
        self.inside_tbody = False
        self.title_level = 1

    def depart_document(self, node):
        pass

    def visit_section(self, node):
        self.title_level += 1

    def depart_section(self, node):
        if self.title_level == 4:
            #hardcode the module 
            if self._high_level_flag == [1, 0, 0]:
                self._state_partitions.append(self.get_partitions('states', self.state_module))
            elif self._high_level_flag == [0, 1, 0]:
                self._exchange_partitions.append(self.get_partitions('exchanges', self.exchange_module))
            elif self._high_level_flag == [0, 0, 1]:
                self._transitions += self.get_transition(self.state_module, self.exchange_module)
            self.full_description = collections.OrderedDict()
            self.standard_methods = {}
            self.codes = []
            self._classname = ''
            self.array_items = []
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
        #flag the low section
        if title == 'Definition and accessibility':
            self._low_level_flag = [1, 0, 0]
        elif  title == 'Value partitions':
            self._low_level_flag = [0, 1, 0]
        elif  title == 'Standard methods' or title == 'Exchange' or title == 'Transitions - exchanges':
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

    def visit_row(self, node):
        if self.inside_tbody == False:
            return
        row = node.astext()
        content = row.split('\n\n')
        if self._high_level_flag == [1, 0, 0] :
            if  self._low_level_flag == [0, 1, 0]:
                id = content[0]
                code = content[1]
                val = content[2]
                com = content[3]
                self.codes.append(code)
                self.full_description[code] = (id, val, com)
            elif self._low_level_flag == [0, 0, 1]:
                code = content[0]
                com = content[1]
                self.standard_methods[code] = getattr(checkmate.state, code)
        elif self._high_level_flag == [0, 1, 0] and self._low_level_flag == [0, 1, 0]:
            id = content[0]
            code = content[1]
            val = content[2]
            com = content[3]
            self.codes.append(code)
            self.full_description[code] = (id, val, com)
        elif self._high_level_flag == [0, 0, 1] and self._low_level_flag == [0, 0, 1]:
            self.array_items.append(content)

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
            for text in texts:
                if not ' ' in text and not '_' in text:
                    self._classname = str(text)
             
    def get_partitions(self, partition_type, _module=None):
        classname = self._classname
        full_description = self.full_description
        self.standard_methods.update({'_valid_values': [checkmate._utils.valid_value_argument(_v) for _v in self.codes if checkmate._utils.valid_value_argument(_v) is not None], '_description': full_description})
        setattr(_module, classname, _module.declare(classname, self.standard_methods))
        setattr(_module, _to_interface(classname), _module.declare_interface(_to_interface(classname), {}))
        zope.interface.classImplements(getattr(_module, classname), [getattr(_module, _to_interface(classname))])
        interface = getattr(_module, _to_interface(classname))
        cls = checkmate._utils.get_class_implementing(interface)
        partition_storage = []
        for code in self.codes:
            if checkmate._utils.is_method(code):
                setattr(_module, checkmate._utils.internal_code(code), functools.partial(cls, checkmate._utils.internal_code(code)))
            if partition_type == 'states':
                storage = checkmate._storage.store_state_value(interface, code)
                partition_storage.append(storage)
                full_description[code] = (storage, full_description[code])
            elif partition_type == 'exchanges':
                storage = checkmate._storage.store_exchange(interface, code)
                full_description[code] = (storage, full_description[code])
                partition_storage.append(storage)
        setattr(cls, '_description', full_description)
        return (interface, partition_storage)

    def get_transition(self, state_module=None, exchange_module=None):
        component_transition = []
        initial_state = []
        initial_state_id = []
        row_count = len(self.array_items)
        array_items = self.array_items
        for i in range(row_count):
            if array_items[i][1] != 'x':
                initial_state_id.append(i)
                if array_items[i][0] == 'x':
                    continue
                interface = getattr(state_module, _to_interface(array_items[i][0]))
                cls = checkmate._utils.get_class_implementing(interface)
                initial_state.append((interface, array_items[i][1]))
                if checkmate._utils.is_method(array_items[i][1]):
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(state_module, checkmate._utils.internal_code(array_items[i][1]), functools.partial(cls, checkmate._utils.internal_code(array_items[i][1])))
        for i in range(2, len(array_items[0])):
            input = []
            for j in range(0, initial_state_id[0]):
                if array_items[j][i] != 'x':
                    interface = getattr(exchange_module, _to_interface(array_items[j][0]))
                    input.append((interface, array_items[j][i]))
                    if exchange_module is not None:
                        cls = checkmate._utils.get_class_implementing(interface)
                        setattr(exchange_module, checkmate._utils.internal_code(array_items[j][i]), functools.partial(cls, checkmate._utils.internal_code(array_items[j][i])))
            final = []
            for j in range(initial_state_id[0], initial_state_id[-1]+1):
                if array_items[j][0] == 'x':
                    continue
                interface = getattr(state_module, _to_interface(array_items[j][0]))
                final.append((interface, array_items[j][i]))
            output = []
            for j in range(initial_state_id[-1]+1, row_count):
                if array_items[j][i] != 'x':
                    interface = getattr(exchange_module, _to_interface(array_items[j][0]))
                    output.append((interface, array_items[j][i]))
                    if exchange_module is not None:
                        cls = checkmate._utils.get_class_implementing(interface)
                        setattr(exchange_module, checkmate._utils.internal_code(array_items[j][i]), functools.partial(cls, checkmate._utils.internal_code(array_items[j][i])))
            t = checkmate.transition.Transition(initial=initial_state, incoming=input, final=final, outgoing=output)
            component_transition.append(t)
        return component_transition


def call_visitor(content, state_module=None, exchange_module=None):
    """

        >>> import sample_app.exchanges
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> output = call_visitor(c, exchange_module=sample_app.exchanges)
        >>> output['exchanges'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.exchanges.IAction>, [<checkmate._storage.ExchangeStorage object at ...
        >>> len(output['exchanges'])
        2
        >>> import sample_app.component_1.states
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/sample_app/component_1/state_machine.rst'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> output = call_visitor(c, state_module=sample_app.component_1.states, exchange_module=sample_app.exchanges)
        >>> output['states'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.component_1.states.IState>, [<checkmate._storage.StateStorage object at ...
        >>> len(output['states'])
        2
    """
    dt = docutils.core.publish_doctree(source=content)
    wt = Writer(dt, state_module, exchange_module)
    wt.translate()
    return {'states': wt.visitor._state_partitions,
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

