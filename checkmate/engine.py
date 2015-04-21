# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.


import checkmate.parser.yaml_visitor
import checkmate.partition_declarator


class Engine(object):
    # This is Transition Engine
    def __init__(self, data_structure_module, exchange_module,
                 state_module, source_filenames):
        declarator = checkmate.partition_declarator.Declarator(
            data_structure_module,
            exchange_module=exchange_module,
            state_module=state_module)
        define_data = ''
        for _f in source_filenames:
            with open(_f, 'r') as _file:
                define_data += _file.read()
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        declarator.new_definitions(data_source)
        declarator_output = declarator.get_output()
        self.states = declarator_output['states']
        self.blocks = declarator_output['transitions']
        self.services = {}
        self.service_classes = []
        self.communication_list = set()
        for _b in self.blocks:
            for _i in _b.incoming:
                _ex = _i.factory()
                if _i.code not in self.services:
                    self.services[_i.code] = _ex
                if _i.partition_class not in self.service_classes:
                    self.service_classes.append(_i.partition_class)
                self.communication_list.add(_ex.communication)
            for _o in _b.outgoing:
                _ex = _o.factory()
                self.communication_list.add(_ex.communication)

    def block_by_name(self, name):
        for _b in self.blocks:
            if _b.name == name:
                return _b

    def set_owner(self, name):
        for _b in self.blocks:
            _b.owner = name

    def get_blocks_by_input(self, exchange, states):
        block_list = []
        for _b in self.blocks:
            if (_b.is_matching_incoming(exchange, states) and
                    _b.is_matching_initial(states)):
                block_list.append(_b)
        return block_list

    def get_blocks_by_output(self, exchange, states):
        for _b in self.blocks:
            if (_b.is_matching_outgoing(exchange) and
                    _b.is_matching_initial(states)):
                return _b
        return None
