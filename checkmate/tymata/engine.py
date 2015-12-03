# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os

import checkmate.tymata.visitor
import checkmate.tymata.transition


def get_definition_data(definitions):
    definition_data = ''
    if type(definitions) != list:
        definitions = [definitions]
    for _d in definitions:
        if os.path.isfile(_d):
            with open(_d, 'r') as _file:
                definition_data += _file.read()
        elif os.path.isdir(_d):
            for (dirpath, dirnames, filenames) in os.walk(_d):
                for _file in filenames:
                    if _file.endswith(".yaml"):
                        with open(os.path.join(dirpath, _file), 'r') as _file:
                            definition_data += _file.read()
    return definition_data


def get_blocks_from_data(exchange_module, state_module, define_data):
    items = checkmate.tymata.visitor.call_visitor(define_data)
    blocks = []
    for _item in items:
        new_block = checkmate.tymata.transition.make_transition(_item,
                        [exchange_module], [state_module])
        blocks.append(new_block)
    return blocks


class AutoMata(object):
    # This is Transition Engine
    def __init__(self, exchange_module,
                 state_module, class_file, instance_dir=None):
        definitions = []
        if instance_dir:
            definitions.append(instance_dir)
        if class_file:
            definitions.append(class_file)
        define_data = get_definition_data(definitions)
        self.blocks = get_blocks_from_data(exchange_module,
                        state_module, define_data)
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

    def process(self, exchange, states, default, block=None):
        if block is None:
            _block = self.get_blocks_by_input(exchange, states)[0]
        else:
            _block = block
        return _block, _block.process(states, exchange, default=default)

    def simulate(self, block, states, default):
        _incoming = block.generic_incoming(states)
        output = []
        for _o in block.process(states, _incoming, default=default):
            if (_incoming and isinstance(_o, _incoming[0].return_type)):
                continue
            output.append(_o)
        return output
