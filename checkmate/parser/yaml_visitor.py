import yaml
import collections

import checkmate.state


class Visitor():
    exchanges_kind_list = ["Standard methods", "Exchange", "Transitions", "Procedures"]
    definition_kind_list = ["Definition and accessibility", "Definition"]

    def __init__(self, stream):
        """
            >>> import os
            >>> import checkmate.parser.yaml_visitor
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
            >>> file=open(input_file,'r')
            >>> c = file.read()
            >>> visitor = checkmate.parser.yaml_visitor.Visitor(c)
            >>> len(visitor._data_structure_partitions)
            3
            >>> len(visitor._exchange_partitions)
            2
        """
        self._state_partitions = []
        self._data_structure_partitions = []
        self._exchange_partitions = []
        self._transitions = []

        self.full_description = collections.OrderedDict()
        self._classname = ''
        self.codes = []
        self.tran_items = []
        self.standard_methods = {}

        self.read_document(stream)

    def read_document(self, stream):
        for each in yaml.load_all(stream):
            self.parser_chunk(each)

    def parser_chunk(self, chunk):
        """
            >>> import os
            >>> import yaml
            >>> import checkmate.parser.yaml_visitor
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
            >>> f = open(input_file,'r')
            >>> c1 = f.read()
            >>> f.close()
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
            >>> f = open(input_file,'r')
            >>> c2 = f.read()
            >>> f.close()
            >>> visitor = checkmate.parser.yaml_visitor.Visitor(c1)
            >>> len(visitor._state_partitions)
            0
            >>> list(yaml.load_all(c2))[0]['title']
            'State identification'
            >>> visitor.parser_chunk(list(yaml.load_all(c2))[0])
            >>> len(visitor._state_partitions)
            2
            >>> len(visitor._transitions)
            0
            >>> list(yaml.load_all(c2))[1]['title']
            'State machine'
            >>> visitor.parser_chunk(list(yaml.load_all(c2))[1])
            >>> len(visitor._transitions)
            4
        """
        title = chunk['title']
        chunk_data = chunk['data']
        for _d in chunk_data:
            for inside_title in _d:
                if inside_title in self.definition_kind_list:
                    self.definition_and_accessibility(_d[inside_title])

            if title == "State identification":
                self.state_identification(_d)
                self._state_partitions.append({'clsname': self._classname,
                                                'standard_methods': self.standard_methods,
                                                'codes': self.codes,
                                                'full_desc': self.full_description})
            elif title == "Data structure":
                self.data_structure(_d)
                self._data_structure_partitions.append({'clsname': self._classname,
                                                'standard_methods': self.standard_methods,
                                                'codes': self.codes,
                                                'full_desc': self.full_description})
            elif title == "Exchange identification":
                self.exchange_identification(_d)
                self._exchange_partitions.append({'clsname': self._classname,
                                                'standard_methods': self.standard_methods,
                                                'codes': self.codes,
                                                'full_desc': self.full_description})
            elif title == "State machine" or title == "Test procedure":
                self.state_machine_or_test_procedure(_d)
                self._transitions.extend(self.tran_items)

            self.full_description = collections.OrderedDict()
            self._classname = ''
            self.codes = []
            self.tran_items = []
            self.standard_methods = {}

    def state_identification(self, content):
        for _k,_v in content.items():
            if _k in self.exchanges_kind_list:
                self.dentification_exchanges(_v)
            if _k == "Value partitions":
                self.value_partitions(_v)

    def exchange_identification(self, content):
        for _k,_v in content.items():
            if _k == "Value partitions":
                self.value_partitions(_v)

    def state_machine_or_test_procedure(self, content):
        for _k,_v in content.items():
            if _k in self.exchanges_kind_list:
                self.tran_items.extend(_v)

    def data_structure(self, content):
        for _k,_v in content.items():
            if _k == "Value partitions":
                self.value_partitions(_v)

    def definition_and_accessibility(self, data):
        self._classname = data

    def value_partitions(self, data):
        for _list in data:
            id = _list[0]
            code = _list[1]
            val = _list[2]
            com = _list[3]
            self.codes.append(code)
            self.full_description[code] = (id, val, com)

    def dentification_exchanges(self, data):
        for _list in data:
            code = _list[0]
            com = _list[1]
            # Add standard member function to class
            try:
                self.standard_methods[code] = getattr(checkmate.state, code)
            except AttributeError:
                raise AttributeError(checkmate.state.__name__+' has no method defined: '+code)


def call_visitor(stream):
    """
        >>> import sample_app.exchanges
        >>> import sample_app.data_structure
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> output = call_visitor(c)
        >>> len(output['data_structure'])
        3
        >>> len(output['exchanges'])
        2
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> output = call_visitor(c)
        >>> len(output['states'])
        2
    """
    visitor = Visitor(stream)
    return {'states': visitor._state_partitions,
            'data_structure': visitor._data_structure_partitions,
            'exchanges': visitor._exchange_partitions,
            'transitions': visitor._transitions}
