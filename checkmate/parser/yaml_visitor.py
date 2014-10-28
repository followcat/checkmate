import yaml
import collections


class Visitor():
    exchanges_kind_list = ["Exchange", "Transitions", "Procedures"]
    definition_kind_list = ["Definition and accessibility", "Definition"]

    def __init__(self, define_content, value_content):
        """
            >>> import os
            >>> import checkmate.parser.yaml_visitor
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
            >>> file1=open(input_file,'r')
            >>> c1 = file1.read()
            >>> file1.close()
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/test_value.yaml'
            >>> file2=open(input_file,'r')
            >>> c2 = file2.read()
            >>> file2.close()
            >>> visitor = checkmate.parser.yaml_visitor.Visitor(c1, c2)
            >>> len(visitor._data_structure_partitions)
            1
            >>> len(visitor._exchange_partitions)
            2
        """
        self._state_partitions = []
        self._data_structure_partitions = []
        self._exchange_partitions = []
        self._transitions = []

        self.full_description = collections.OrderedDict()
        self._classname = ''
        self.codes_list = []
        self.values_list = []
        self.code_value_list = []
        self.tran_items = []

        self.read_document(define_content, value_content)

    def read_document(self, define_content, value_content):
        if value_content is not None:
            value_content = yaml.load(value_content)
        for each in yaml.load_all(define_content):
            self.parser_chunk(each, value_content)

    def parser_chunk(self, chunk, data):
        """
            >>> import os
            >>> import yaml
            >>> import checkmate.parser.yaml_visitor
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
            >>> f = open(input_file,'r')
            >>> c1 = f.read()
            >>> f.close()
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/test_value.yaml'
            >>> f = open(input_file,'r')
            >>> c2 = f.read()
            >>> f.close()
            >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
            >>> f = open(input_file,'r')
            >>> c3 = f.read()
            >>> f.close()
            >>> visitor = checkmate.parser.yaml_visitor.Visitor(c1, c2)
            >>> len(visitor._state_partitions)
            0
            >>> visitor._data_structure_partitions[0]['codes_list']
            ['R1']
            >>> visitor._data_structure_partitions[0]['values_list']
            [['AT1', 'NORM']]
            >>> list(yaml.load_all(c3))[0]['title']
            'State identification'
            >>> visitor.parser_chunk(list(yaml.load_all(c3))[0], None)
            >>> len(visitor._state_partitions)
            2
            >>> len(visitor._transitions)
            0
            >>> list(yaml.load_all(c3))[1]['title']
            'State machine'
            >>> visitor.parser_chunk(list(yaml.load_all(c3))[1], None)
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
                                                'codes_list': self.codes_list,
                                                'values_list': self.values_list,
                                                'code_value_list': self.code_value_list,
                                                'full_desc': self.full_description})
            elif title == "Data structure":
                self.data_structure(data)
                self._data_structure_partitions.append({'clsname': self._classname,
                                                'codes_list': self.codes_list,
                                                'values_list': self.values_list,
                                                'code_value_list': self.code_value_list,
                                                'full_desc': self.full_description})
            elif title == "Exchange identification":
                self.exchange_identification(_d)
                self._exchange_partitions.append({'clsname': self._classname,
                                                'codes_list': self.codes_list,
                                                'values_list': self.values_list,
                                                'code_value_list': self.code_value_list,
                                                'full_desc': self.full_description})
            elif title == "State machine" or title == "Test procedure":
                self.state_machine_or_test_procedure(_d)
                self._transitions.extend(self.tran_items)

            self.full_description = collections.OrderedDict()
            self._classname = ''
            self.codes_list = []
            self.values_list = []
            self.tran_items = []
            self.code_value_list = []

    def state_identification(self, content):
        for _k, _v in content.items():
            if _k == "Value partitions":
                codes_list, values_list, code_value_list = self.value_partitions(_v)
                self.codes_list.extend(codes_list)
                self.values_list.extend(values_list)
                self.code_value_list.extend(code_value_list)

    def exchange_identification(self, content):
        for _k, _v in content.items():
            if _k == "Value partitions":
                codes_list, values_list, code_value_list = self.value_partitions(_v)
                self.codes_list.extend(codes_list)
                self.values_list.extend(values_list)
                self.code_value_list.extend(code_value_list)

    def state_machine_or_test_procedure(self, content):
        for _k, _v in content.items():
            if _k in self.exchanges_kind_list:
                self.tran_items.extend(_v)

    def data_structure(self, data):
        if self._classname in data:
            content = data.get(self._classname)
        for _l in content:
            code = _l[0]
            val = _l[1]
            self.codes_list.append(code)
            self.values_list.append(val)
            self.code_value_list.append((code, val))

    def definition_and_accessibility(self, data):
        self._classname = data

    def value_partitions(self, data):
        codes_list = []
        values_list = []
        code_value_list = []
        for _list in data:
            id = _list[0]
            code = _list[1]
            val = _list[2]
            com = _list[3]
            codes_list.append(code)
            values_list.append(val)
            code_value_list.append((code, val))
            self.full_description[code] = (id, com)
        return codes_list, values_list, code_value_list


def call_visitor(define_content, value_content=None):
    """
        >>> import os
        >>> import checkmate.parser.yaml_visitor
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
        >>> f1 = open(input_file,'r')
        >>> c1 = f1.read()
        >>> f1.close()
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/test_value.yaml'
        >>> f2 = open(input_file,'r')
        >>> c2 = f2.read()
        >>> f2.close()
        >>> output = checkmate.parser.yaml_visitor.call_visitor(c1, c2)
        >>> len(output['data_structure'])
        1
        >>> len(output['exchanges'])
        2
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> output = checkmate.parser.yaml_visitor.call_visitor(c)
        >>> len(output['states'])
        2
    """
    visitor = Visitor(define_content, value_content)
    return {'states': visitor._state_partitions,
            'data_structure': visitor._data_structure_partitions,
            'exchanges': visitor._exchange_partitions,
            'transitions': visitor._transitions}
