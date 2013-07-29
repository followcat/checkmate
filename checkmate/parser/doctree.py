"""
this module contains method the create a document and add kinds of nodes in it
"""

import docutils.nodes
import docutils.utils
import os
import re
import os.path
import collections


def get_section(source):
    if type(source)!= collections.OrderedDict and type(source)!= dict:
        return None

    sibling = []
    for key in source.keys():
        if type(key) == str:
            title = key 
            _section = docutils.nodes.section(names=re.sub("\\s",'-', title.strip()), ids=title.strip())
            _title = docutils.nodes.title()
            _title.extend([docutils.nodes.Text(title)])
            _section.append(_title)
            fill_section(source[key], _section)
            sibling.append(_section)
    return sibling


def fill_section(value, _section):
    if type(value) == str:
        _text = value
        #ADD paragraph
        _paragraph = docutils.nodes.paragraph()
        _paragraph.extend([docutils.nodes.Text(_text)])
        _section.append(_paragraph)
    elif type(value) == tuple:
        _table = value
        #ADD table
        _section.append(get_table(_table))
    elif type(value) == list:
        _list = value
        #ADD list
        _section.extend(get_list(_list))
    elif type(value) == collections.OrderedDict or type(value) == dict:
        _section.extend(get_section(value))


def get_list(_list):
    if type(_list) != list or len(_list) < 1:
        return None
    _return_list = []
    for item in _list:
        if type(item) == str:
            _return_list.append(get_text(item))
        elif type(item) == tuple:
            _return_list.append(get_table(item))
    return _return_list


def get_text(text):
    if type(text) != str:
        return None
    _paragraph = docutils.nodes.paragraph()
    _paragraph.extend([docutils.nodes.Text(text)])
    return _paragraph


def get_table(table):
    """
    """
    if type(table) != tuple or len(table) != 2:
        return None
    if type(table[0]) != list:
        return None
    _table = docutils.nodes.table()
    header = table[0]
    body = table[1]
    col_length = []
    text_length = []
    for table_line in [header] + body:
        oversize = (len(table_line) - len(text_length)) 
        if oversize > 0:
                text_length.extend([0] * oversize)
        column = 0
        for text in table_line:
            size = len(text.rstrip()) + 2
            if size > text_length[column]:
                text_length[column] = size
            column += 1
    if len(text_length)>0:
        _tgroup = docutils.nodes.tgroup(cols=len(text_length))
    for col_width in text_length:
        _colspec = docutils.nodes.colspec(colwidth=col_width)
        _tgroup.append(_colspec)
    if len(header)>0:
        _thead = docutils.nodes.thead()
        _tgroup.append(_thead)
        # fill the table header
        header_column = len(header)
        _row = docutils.nodes.row()
        column = 0
        add_blank_cells = len(text_length) - len(header)
        if add_blank_cells > 0:
            header += ' '*add_blank_cells
        for text in header:
            _entry = docutils.nodes.entry()
            if(len(text)>0):
                _paragraph = docutils.nodes.paragraph()
                _paragraph.extend([docutils.nodes.Text(text.strip())])
                _entry.append(_paragraph)
            column = column + 1
            _row.append(_entry)
        _thead.append(_row)

    if len(body)>0:
        _tbody = docutils.nodes.tbody()
        _tgroup.append(_tbody)
        for table_row in body:
            _row = docutils.nodes.row()
            column = 0
            add_blank_cells = len(text_length) - len(table_row)
            if add_blank_cells > 0:
                table_row += ' '*add_blank_cells
            for text in table_row:
                _entry = docutils.nodes.entry()
                if(len(text)>0):
                    _paragraph = docutils.nodes.paragraph()
                    _paragraph.extend([docutils.nodes.Text(text.strip())])
                    _entry.append(_paragraph)
                column = column + 1
                _row.append(_entry)
            _tbody.append(_row)
    _table.append(_tgroup)
    return _table


def get_document(source):
    """
    >>> import collections
    >>> a = collections.OrderedDict([('Procedure identification', collections.OrderedDict([('Procedure', collections.OrderedDict([('Implementation', ([], [['path', '/home/vcr/Projects/Checkmate/test_procedures.py'], ['class', 'TestProcedure'], ['Setup procedure', 'TestSetup'], ['Teardown procedure', 'TestTeardown']])), ('Initial state', ['this is a text paragraph', 'this is another text paragraph', ([], [['Any of the states', 'Q0()'], ['Any of the states', 'M0(AUTO)'], ['Any of the states', 'R0(0)']])]), ('Final state', ([], [['Any of the states', 'Q0()'], ['Any of the states', 'M0(MANUAL)'], ['Any of the states', 'R0(0)']])), ('Test partition', (['Info exchange', 'Origin', 'Destination', 'Comment'], [['TM()', 'mcrhci', 'abs', 'HCI toggle request'], ['ST()', 'abs', 'mcrhci', 'Beam scheduler publish state']]))]))]))])
    >>> doctree = get_document(a)
    >>> import visitor
    >>> f2 = open('test.rst', 'w')
    >>> import docutils.core
    >>> dt = doctree 
    >>> import visitor
    >>> wt = visitor.Writer()
    >>> wt.write(document=dt, destination=f2)
    1965
    >>> f2.close()


    """
    if len(source) <= 0:
        return None
    Heading_Level = 3
    _doctree = docutils.utils.new_document(source_path="New Document")
    _entry_section = None
    for fill_in_title in range(1, Heading_Level):
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
    _entry_section.extend(get_section(source))
    return _doctree
