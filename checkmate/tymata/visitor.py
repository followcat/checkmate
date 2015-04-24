# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import yaml
import collections

import checkmate._yaml


class Visitor():
    def __init__(self, content):
        self._transitions = []
        content = self.pre_process(content)
        self.read_document(content)

    def pre_process(self, content):
        lines = content.split('\n')
        for index, line in enumerate(lines):
            if '@from_' in line:
                lines[index] = lines[index].replace('@from_', '')
        return '\n'.join(lines)

    def read_document(self, content):
        for each in yaml.load_all(content, Loader=checkmate._yaml.Loader):
            self.parser_chunk(each)

    def parser_chunk(self, chunk):
        title = chunk['title']
        for _d in chunk['data']:
            if title == "State machine" or title == "Test procedure":
                for _k, _v in _d.items():
                    self._transitions.extend(_v)


def call_visitor(content):
    visitor = Visitor(content)
    return collections.OrderedDict([('transitions', visitor._transitions)])


def data_from_files(application):
    """"""
    state_modules = []
    for name in list(application.components.keys()):
        state_modules.append(application.components[name].state_module)
    paths = application.itp_definition
    if type(paths) != list:
        paths = [paths]
    array_list = []
    try:
        matrix = ''
        for path in paths:
            if not os.path.isdir(path):
                continue
            with open(os.sep.join([path, "itp.yaml"]), 'r') as _file:
                matrix += _file.read()
    except FileNotFoundError:
        return []
    _output = call_visitor(matrix)
    for data in _output['transitions']:
        array_list.append(data)
    return array_list
