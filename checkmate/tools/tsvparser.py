# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

"""
to use this script, type:
python tsvparser.py **.tsv
that will generate a **.rst file with coverse from **.tsv to doctree to **.rst
"""

import re
import os
import os.path
import docutils.parsers
import docutils.nodes
import docutils.utils
import optparse
import configparser

import checkmate.parser.rst_writer


def open_file(filename):
    try:
        return open(filename)
    except:
        if os.path.isfile(filename):
            print("Problem opening input file %s." %(filename))
        else:
            print("%s is not a file." %(filename))
        sys.exit(-1)

class TsvConfigParser(configparser.ConfigParser):
    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self._section = 'Default tsv'
        self.add_section(self._section)
        self.set(self._section, 'table_length', '85')
        self.set(self._section, 'highest_section', '3')
        self.set(self._section, 'number_of_sections', '3')
        self.set(self._section, 'rst_marker_1', '=')
        self.set(self._section, 'rst_marker_2', '-')
        self.set(self._section, 'rst_marker_3', '+')
        self.set(self._section, 'rst_marker_4', '*')
        self.set(self._section, 'rst_marker_5', '^')

    def get_table_length(self):
        return self.getint(self._section, 'table_length')

    def get_highest_section(self):
        return self.getint(self._section, 'highest_section')

    def get_number_of_sections(self):
        return self.getint(self._section, 'number_of_sections')

    def get_lowest_section(self):
        return (self.getint(self._section, 'highest_section')
                + self.getint(self._section, 'number_of_sections') - 1)

    def get_rst_marker(self, section):
        if section == 4:
            return self.get(self._section, 'rst_marker_4')
        elif section == 3:
            return self.get(self._section, 'rst_marker_3')
        elif section == 2:
            return self.get(self._section, 'rst_marker_2')
        elif section == 1:
            return self.get(self._section, 'rst_marker_1')
        elif section == 5:
            return self.get(self._section, 'rst_marker_5')
        else:
            return ''

class TsvOptionParser(optparse.OptionParser):
    def set_options(self):
        self.add_option('-c', '--config', dest='config_filename',
                        metavar='FILE', default="odt.ini",
                        help="name of the ini file defining configuration")

class TsvLine(object):
    def __init__(self, line):
        self._text = line
        self._type = 'unknown'
        self._subtype = False

    def __str__(self):
        if self._subtype == False:
            return re.sub(os.linesep,'',self._text) + ' ' + self._type
        else:
            return re.sub(os.linesep,'',self._text) + ' ' + self._type + '%i'%self._subtype

    def is_empty(self):
        return self._text == os.linesep

    def is_formating_rule(self):
        return re.search(r'\{.*\}', self._text) != None

    def is_table(self):
        return re.search(r'\t', self._text) != None

    def get_formating_rule(self):
        """
        >>> l = TsvLine("{table heading_lines 4}")
        >>> l.get_formating_rule()
        {'table': {'heading_lines': '4'}}
        """
        if not self.is_formating_rule():
            return {}
        rule_items = re.match('\{(?P<class>\w*) (?P<item>\w*) (?P<value>\w*)\}', self._text)
        try:
            return {rule_items.group('class'):
                        {rule_items.group('item'): rule_items.group('value')}}
        except:
            return {}

    def set_empty(self):
        self._type = 'empty'

    def set_heading(self, level):
        self._type = 'heading'
        self._subtype = level

    def set_table(self, header):
        self._type = 'table'
        self._subtype = header

    def set_formating_rule(self):
        self._type = 'format'
        self._subtype = False


class TsvAnnotatedBuffer(list):
    def __init__(self, config=None):
        list.__init__(self)
        if config == None:
            config = TsvConfigParser()
        self._lowest_heading = config.get_lowest_section()
        self._highest_heading = config.get_highest_section()
        self._current_heading = self._highest_heading
        self._preceeding_empty_lines = 0
        self._in_table = False
        self._table_heading_lines = 0
        self._rules = {}

    def _get_heading(self):
        if self._preceeding_empty_lines > 0:
            self._current_heading = (self._lowest_heading + 1
                                     - self._preceeding_empty_lines)
        elif self._preceeding_empty_lines == 0:
            self._current_heading = self._current_heading + 1
        # Too many empty lines
        if self._current_heading < self._highest_heading:
            self._current_heading = self._highest_heading
        return self._current_heading    

    def _get_table_header_end(self, index):
        """Returns if the line given by index is the last of the table header.

        >>> b = TsvAnnotatedBuffer()
        >>> b.append("{table heading_lines 4}")
        >>> b.append("me\\tyou\\n")
        >>> b.append("me2\\tyou2\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.update()
        >>> b._rules
        {'table': {'heading_lines': '2'}}
        >>> b.trace()
        {table heading_lines 2} format
        me        you heading4
        me2       you2 heading5
        me3       you3 unknown
        """
        if index >= len(self)-1:
            return False
        elif not self[index+1].is_table():
            self._table_heading_lines = 0
            return False
        elif ('table' in self._rules
          and 'heading_lines' in self._rules['table']):
            if (self._table_heading_lines <=
                    int(self._rules['table']['heading_lines'])-1):
                self._table_heading_lines += 1
                return True
        else:
            if self._table_heading_lines == 0:
                self._table_heading_lines += 1
                return True
        return False

    def _is_lowest_heading(self):
        return self._current_heading >= self._lowest_heading

    def append(self, line):
        list.append(self, TsvLine(line))

    def add_rule(self, rule):
        """Add a formating rule.

        >>> c= TsvConfigParser()
        >>> b = TsvAnnotatedBuffer(c)
        >>> b.add_rule({'table': {'heading_lines': '2'}})
        >>> b._rules
        {'table': {'heading_lines': '2'}}
        >>> b.add_rule(TsvLine("{table heading_lines 4}").get_formating_rule())
        >>> b._rules
        {'table': {'heading_lines': '4'}}
        """
        self._rules.update(rule)

    def clear_rules(self, rule_class):
        if rule_class in self._rules:
            self._rules.pop(rule_class)

    def update(self):
        """
        >>> from tsvparser import *
        >>> config = TsvConfigParser()
        >>> _buffer = TsvAnnotatedBuffer(config)
        >>> _buffer.append('Internal storage\\n')
        >>> _buffer.append('LoginName\\n')
        >>> _buffer.append('Value partitions\\n')
        >>> _buffer.append('Some text\\n')
        >>> _buffer.append('\\n')
        >>> _buffer.append('\\n')
        >>> _buffer.append('LoginName\\n')
        >>> _buffer.append('Value partitions\\n')
        >>> _buffer.append('Some text\\n')
        >>> _buffer.update()
        >>> _buffer.trace()
        Internal storage heading3
        LoginName heading4
        Value partitions heading5
        Some text unknown
         empty
         empty
        LoginName heading4
        Value partitions heading5
        Some text unknown
        """
        index = 0
        for line in self:
            if line.is_formating_rule():
                self.add_rule(line.get_formating_rule())
                line.set_formating_rule()
            elif index == 0:
                if line.is_table():
                    line.set_table(self._get_table_header_end(index))
                    self._in_table = True
                else:
                    line.set_heading(self._highest_heading)
            else:
                if line.is_empty():
                    line.set_empty()
                    self._preceeding_empty_lines = self._preceeding_empty_lines + 1
                    self._in_table = False
                    self.clear_rules('table')
                else:
                    if self._preceeding_empty_lines != 0:
                        line.set_heading(self._get_heading())
                        self._preceeding_empty_lines = 0
                    else:
                        if line.is_table():
                            line.set_table(self._get_table_header_end(index))
                            self._in_table = True
                        else:
                            if self._in_table:
                                line.set_heading(self._current_heading)
                            else:
                                if (not self._is_lowest_heading()
                                  and (index != len(self)-1)
                                  and not self[index+1].is_empty()):
                                    line.set_heading(self._get_heading())
                            self._in_table = False
            index = index + 1

    def trace(self):
        for line in self:
            print('%s'%line)

class RstWriter(object):
    def __init__(self, config=None):
        if config == None:
            config = TsvConfigParser()
        self._config = config
        self._index_increment = 0
        self._income_source = '' 
        self._section_index = 0
        self._section_increment = 0
        self._empty_line = 0

    def format_unknown(self, line, index, _buffer):
        """

        >>> b = TsvAnnotatedBuffer()
        >>> b.append("meyou1\\n")
        >>> b.append("meyou2\\n")
        >>> b.append("meyou3\\n")
        >>> b.append("meyou4\\n")
        >>> b.append("meyou5\\n")
        >>> b.trace()
        >>> w = RstWriter()
        >>> output = w.format_unknown(b[0], 0, b)
        >>> output.traverse()

        """
        if index >= len(_buffer)-1:
            pass
        text_end_index = len(_buffer) - (index+1)
        text_lines = []
        for text_index in range(index, len(_buffer)):
            text_line = _buffer[text_index]
            if not text_line._type == 'unknown':
                text_end_index = text_index - (index+1)
                break
            text_lines.append(text_line._text)
        _text = docutils.nodes.Text(''.join(text_lines).rstrip())
        _paragraph = docutils.nodes.paragraph()
        _paragraph.append(_text)
        self._index_increment = text_end_index
        return _paragraph

    def format_heading(self, line, index, _buffer):
        """
        >>> import docutils.nodes
        >>> b = TsvAnnotatedBuffer()
        >>> b.append("meyou\\n")
        >>> b.append("me2you2\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("me3\\tyou3\\n")
        >>> b.append("\\n")
        >>> b.append("me2you2\\n")
        >>> b.append("2th---2th---me2you2\\n")
        >>> b.append("3rd---3rd---3rd---me2you2\\n")
        >>> b.append("\\n")
        >>> b.update()
        >>> b.trace()
        >>> w = RstWriter()
        >>> output = w.format_heading(b[0], 0, b)
        >>> output.get('names')
        'meyou'
        >>> output.get('ids')
        'meyou'
        >>> w._section_index
        >>> output.traverse()
        >>> f1 = file('section.xml', 'w')
        >>> output.asdom().writexml(f1)
        >>> f1.close()
        """
        _begin_index = index
        _section = docutils.nodes.section(names=re.sub("\\s",'-',line._text.strip()), ids=line._text.strip())
        _text = docutils.nodes.Text(line._text.strip())
        _title = docutils.nodes.title()
        _title.append(_text)
        _section.append(_title)
        while index<(len(_buffer)-1): 
            index += 1
            self._section_increment = index - _begin_index
            line = _buffer[index]
            if line._type == 'format':
                pass
            elif line._type == 'heading':
                _subsection = self.format_heading(_buffer[index], index, _buffer)
                index = self._section_index
                _section.append(_subsection)
            elif line._type == 'table':
                _table = self.format_table(_buffer[index], index, _buffer)
                self._section_index += self._index_increment
                index += self._index_increment
                _section.append(_table)
            elif line._type == 'unknown':
                _text = self.format_unknown(_buffer[index], index, _buffer)
                self._section_index += self._index_increment
                index += self._index_increment
                _section.append(_text)
            else:
                self._empty_line += 1
                self._section_index = index 
                self._section_increment = index - _begin_index
                return _section
        self._section_index = index 
        self._section_increment = index - _begin_index
        return _section

    def format_table(self, line, index, _buffer):
        """

        >>> b = TsvAnnotatedBuffer()
        >>> b.append("me\\tyou\\n")
        >>> b.update()
        >>> w = RstWriter()
        >>> output = w.format_table(b[0], 0, b)
        >>> b = TsvAnnotatedBuffer()
        >>> b.append("me\\tyou\\n")
        >>> b.append("me2\\tyou2\\n")
        >>> b.append("me3\\tyoooooooooooooooooooooou3\\n")
        >>> b.append("me3tyoooooooooooooooooooooou3\\n")
        >>> b.update()
        >>> w = RstWriter()
        >>> output2 = w.format_table(b[0], 0, b)
        table end index is 2
        >>> f1 = file('test.xml', 'w')
        >>> output2.asdom().writexml(f1) 
        >>> f1.close()

        """
        _table = docutils.nodes.table()
        if index >= len(_buffer)-1:
            pass
        table_end_index = len(_buffer) - (index+1)
        header = []
        table_content = []
        for table_index in range(index, len(_buffer)):
            table_line = _buffer[table_index]
            if not table_line._type == 'table':
                table_end_index = table_index - (index+1)
                break
            if table_line._subtype:
                header.append(table_line._text)
            else:
                table_content.append(table_line._text)
                #print table_line._text

        text_length = []
        for table_line in (header + table_content):
            oversize = (len(table_line.split('\t'))
                        - len(text_length))
            if oversize > 0:
                text_length.extend([0] * oversize)
            column = 0
            for text in table_line.split('\t'):
                size = len(text.rstrip()) + 2
                if size > text_length[column]:
                    text_length[column] = size 
                column += 1
        if len(text_length)>0:
            _tgroup = docutils.nodes.tgroup(cols=len(text_length))
        #_tgroup = docutils.nodes.tgroup(cols=len(text_length))
        for col_width in text_length:
            _colspec = docutils.nodes.colspec(colwidth=col_width)
            _tgroup.append(_colspec)

        header_column=0
        if len(header)>0:
            _thead = docutils.nodes.thead()
            _tgroup.append(_thead)
        for line in header:
            header_column = len(header[0].split('\t'))
            _row = docutils.nodes.row() 
            column = 0
            add_blank_cells = len(text_length) - len(line.split('\t'))
            if add_blank_cells > 0:
                line += '\t'*add_blank_cells
            for text in line.split('\t'):
                _entry = docutils.nodes.entry()
                if(len(text)>0):
                    _text = docutils.nodes.Text(text.strip())
                    _paragraph = docutils.nodes.paragraph()
                    _paragraph.append(_text)
                    _entry.append(_paragraph)
                column = column + 1
                _row.append(_entry)
            _thead.append(_row)

        if len(table_content)>0:
            _tbody = docutils.nodes.tbody()
            _tgroup.append(_tbody)
        for table_row in table_content:
            _row = docutils.nodes.row() 
            column = 0
            add_blank_cells = len(text_length) - len(table_row.split('\t'))
            if add_blank_cells > 0:
                table_row += '\t'*add_blank_cells
            for text in table_row.split('\t'):
                _entry = docutils.nodes.entry()
                if(len(text)>0):
                    _text = docutils.nodes.Text(text.strip())
                    _paragraph = docutils.nodes.paragraph()
                    _paragraph.append(_text)
                    _entry.append(_paragraph)
                column = column + 1
                _row.append(_entry)
            _tbody.append(_row)
        _table.append(_tgroup)
        self._index_increment = table_end_index
        return _table

    def convert(self, _buffer):
        """
        >>> import docutils.nodes
        >>> import os
        >>> import re
        >>> b = TsvAnnotatedBuffer()
        >>> input = file('states.csv', 'r')
        >>> _buffer = input.readlines()
        >>> input.close()
        >>> ending_tabs = re.compile(r'\\t*'+os.linesep)
        >>> for line in _buffer:
        ...     b.append(re.sub(ending_tabs, os.linesep, line))
        ... 
        >>> b.update()
        >>> b.trace()
        >>> w = RstWriter()
        >>> output = w.convert(b)
        >>> f2 = file('states.rst', 'w')
        >>> import docutils.core
        >>> dt = output
        >>> import checkmate.parser.rst_writer
        >>> wt = checkmate.parser.rst_writer.Writer()
        >>> w._income_source = input.name
        >>> wt.write(document=dt, destination=f2)
        >>> f2.close()
        >>> f1 = file('document.xml', 'w')
        >>> output.asdom().writexml(f1)
        >>> f1.close()
        """
        if type(_buffer) != TsvAnnotatedBuffer:
            return ''

        index = 0
        _doctree = docutils.utils.new_document(source_path=self._income_source)
        _entry_section = None
        for fill_in_title in range(1, self._config.get_highest_section()):
            if fill_in_title == 1:
                text = '[Title]'
                paragraph = "[Next line is not a subtitle]"
                _title = docutils.nodes.title()
                _title.extend([docutils.nodes.Text(text)])
                _paragraph = docutils.nodes.paragraph()
                _paragraph.extend([docutils.nodes.Text(paragraph)])
                _doctree.append(_title)
                _doctree.append(_paragraph)
            else:
                text = '[Heading %i]' %(fill_in_title)
                _section = docutils.nodes.section(names=re.sub("\\s",'-',text.strip()), ids=text.strip())
                _title = docutils.nodes.title()
                _title.extend([docutils.nodes.Text(text)])
                _section.append(_title)
                _entry_section = _section
                #create nested sections to be added to the doctree
                if fill_in_title == 2:
                    _doctree.append(_section)
                else:
                    _entry_section.append(_section)

        line = _buffer[index]
        self.format_buffer(_entry_section, line, index, _buffer)
        return _doctree

    def format_buffer(self, _entry_section, line, index, _buffer):
        while index < len(_buffer):
            line = _buffer[index]
            if line._type == 'format':
                pass
            elif line._type == 'heading':
                self._index_increment = 0
                self._empty_line = 0
                self._section_increment = 0
                _section = self.format_heading(line, index, _buffer)
                if self._section_increment >= 0:
                    index += self._section_increment
                _entry_section.append(_section)
            elif line._type == 'table':
                _table = self.format_table(line, index, _buffer)
                index += self._index_increment
                _entry_section.append(_table)
            elif line._type == 'unknown':
                _text = self.format_unknown(line, index, _buffer)
                index += self._index_increment
                _entry_section.append(_text)
            index += 1
        return _entry_section
                        


class TsvParser(object):
    def __init__(self, config):
        self._processed_buffer = TsvAnnotatedBuffer(config)
        self._writer = RstWriter(config)

    def convert(self, tsv):
        input = open_file(tsv)
        self._writer._income_source = input.name
        output = open(os.path.join(os.path.dirname(tsv),
                                   (os.path.basename(tsv).split(os.extsep)[0]
                                    + os.extsep + 'rst')), 'w')
        _buffer = input.readlines()
        ending_tabs = re.compile(r'\t*'+os.linesep)
        for line in _buffer:
            self._processed_buffer.append(re.sub(ending_tabs, os.linesep, line))

        self._processed_buffer.update()
        wt = checkmate.parser.rst_writer.Writer()
        wt.write(document=self._writer.convert(self._processed_buffer), destination=output)
        #output.write(self._writer.convert(self._processed_buffer))
        output.close()
        

def main():
    option_parser = TsvOptionParser()
    option_parser.set_options()
    config_parser = TsvConfigParser()
    try:
        option_parser.print_usage()
        (options, args) = option_parser.parse_args()
    except:
        option_parser.print_usage()
        sys.exit(-1)
    try:
        print(option_parser.config_filename)
        config_parser.readfp(open(option_parser.config_filename))
    except:
        print("Using default configuration")

    parser = TsvParser(config_parser)
    parser.convert(args[0])
    


if __name__ == '__main__':
    main()

