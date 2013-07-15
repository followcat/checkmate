import re
import functools

import docutils.core
import docutils.nodes

import zope.interface

import checkmate.state
import checkmate.exchange
import checkmate.transition

import checkmate._utils


def _to_interface(_classname):
    return 'I'+_classname

def _is_method(name):
    return (re.compile('\(.*\)').search(name) is not None)

def _filter_list_section(section):
    return [s for s in section.traverse(include_self=False) if type(s) == docutils.nodes.section]

def _filter_section(section):
    return [s for s in section.traverse(include_self=False) if type(s) == docutils.nodes.section][0]

def _filter_title(section):
    return [s for s in section.traverse() if type(s) == docutils.nodes.title][0]

def _filter_table(section):
    return [s for s in section.traverse() if type(s) == docutils.nodes.table][0]

def _filter_body(section):
    return [r for r in section.traverse() if type(r) == docutils.nodes.tbody][0]

def _filter_row(section):
    return [r for r in section.traverse() if type(r) == docutils.nodes.row]

def _filter_paragraph(section):
    return [p for p in section.traverse() if type(p) == docutils.nodes.paragraph]
    
def _filter_system_message(section):
    return [m for m in section.traverse() if type(m) == docutils.nodes.system_message]
    
def _clean_children(sections):
    _copy = sections
    for a in _copy:
        for b in [c for c in a.traverse(include_self=False, siblings=False, descend=True)
                                                    if type(c) == docutils.nodes.section]:
            if b in sections:
                sections.pop(sections.index(b))

def _filter_text(paragraph):
    return unicode(paragraph.traverse()[1])

def is_state_section(section):
    return 'state-identification' in section.get('ids')

def is_exchange_section(section):
    return 'exchange-identification' in section.get('ids')

def is_state_machine_section(section):
    return 'state-machine' in section.get('ids')

def get_definition_section(section):
    return [s for s in _filter_list_section(section)
            if 'Definition' in _filter_text(_filter_title(s))][0]

def get_classname(section):
    #if a duplicate target name message is present, take second paragraph
    if len(_filter_system_message(section)) == 0:
        return _filter_text(_filter_paragraph(section)[0])
    else:
        return _filter_text(_filter_paragraph(section)[1])
        
def get_partition_section(section):
    return [s for s in _filter_list_section(section)
            if 'Value partitions' in _filter_text(_filter_title(s))][0]
        
def get_method_section(section):
    methods = [s for s in _filter_list_section(section)
            if 'Standard methods' in _filter_text(_filter_title(s))]
    if len(methods) == 0:
        return methods
    else:
        return methods[0]
        
def get_transition_section(section):
    return [s for s in _filter_list_section(section)
            if 'Transitions - exchanges' in _filter_text(_filter_title(s))][0]
        
#class Decorator(object):
#    def __init__(self, cls, func):
#        self._class = cls
#        self._func = func
#    def __call__(self, **a):
#        def wrapper(cls, param, args):
#            return cls(param, **args)
#        return wrapper(self._class, self._func.__name__, a)
#
#def DecFunction(**a):
#    """"""
#
def partition_identification(sections, _module=None):
    """
        >>> import docutils.core
        >>> matrix=\"\"\"
        ... [Title]
        ... =======
        ... [Next line is not a subtitle]
        ... 
        ... [Heading 2]
        ... -----------
        ... State identification
        ... +++++++++++++++++++++
        ... State
        ... ******
        ... Definition and accessibility
        ... ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        ... State
        ... 
        ... Value partitions
        ... ^^^^^^^^^^^^^^^^^
        ... 
        ... +---------------+--------+--------------------------+-------------------------------+
        ... | Partition     | State  | Valid value              | Comment                       |
        ... +===============+========+==========================+===============================+
        ... | S-STATE-01    | TRUE   | True valid value         | State true value              |
        ... +---------------+--------+--------------------------+-------------------------------+
        ... | S-STATE-02    | FALSE  | True valid value         | State false value             |
        ... +---------------+--------+--------------------------+-------------------------------+
        ... 
        ... 
        ... Standard methods
        ... ^^^^^^^^^^^^^^^^^
        ... 
        ... +--------+-------------------------------+
        ... | Method | Comment                       |
        ... +========+===============================+
        ... | toggle | Toggle component state        |
        ... +--------+-------------------------------+
        ... 
        ... \"\"\"
        >>> dt = docutils.core.publish_doctree(matrix)
        >>> state_sections = []
        >>> for section in _filter_section(dt):
        ...     if is_state_section(section):
        ...         state_sections = _filter_list_section(section)
        >>> partition_identification(state_sections)
        {u'State': {u'FALSE': (u'True valid value', u'State false value'), u'TRUE': (u'True valid value', u'State true value')}}
    """
    _clean_children(sections)
    partitions = []
    for section in sections:
        #get the title of the simplestate as key of the dictionary
        key = _filter_text(_filter_title(section))
        definition = get_definition_section(section)
        classname = str(get_classname(definition).split('\n')[0])

        partition = get_partition_section(section)
        table = _filter_table(partition)
        body = _filter_body(table)
        values = []
        for row in _filter_row(body):
            content = _filter_paragraph(row)
            code = _filter_text(content[1])
            val = _filter_text(content[2])
            com = _filter_text(content[3])
            if checkmate._utils.method_basename(code) is None:
                values.append(code)

        method = get_method_section(section)
        standard_methods = {}
        if len(method) != 0:
            table = _filter_table(method)
            body = _filter_body(table)
            for row in _filter_row(body):
                content = _filter_paragraph(row)
                code = _filter_text(content[0])
                com = _filter_text(content[1])
                standard_methods[code] = getattr(checkmate.state, code)

        if _module is not None:
            standard_methods.update({'_valid_values': values})
            setattr(_module, classname, _module.declare(classname, standard_methods))
            setattr(_module, _to_interface(classname), _module.declare_interface(_to_interface(classname), {}))
            zope.interface.classImplements(getattr(_module, classname), [getattr(_module, _to_interface(classname))])
            for value in values:
                if _is_method(value):
                    interface = getattr(_module, _to_interface(classname))
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(_module, checkmate._utils.method_basename(value), functools.partial(cls, checkmate._utils.method_basename(value)))
            partitions.append(getattr(_module, classname))
    return partitions

def transition_identification(sections, state_module=None, exchange_module=None):
    """
        >>> import docutils.core
        >>> matrix=\"\"\"
        ... [Title]
        ... =======
        ... [Next line is not a subtitle]
        ... 
        ... [Heading 2]
        ... -----------
        ... State identification
        ... +++++++++++++++++++++
        ... State
        ... ******
        ... Definition and accessibility
        ... ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        ... State
        ... 
        ... Value partitions
        ... ^^^^^^^^^^^^^^^^^
        ... 
        ... +---------------+--------+--------------------------+-------------------------------+
        ... | Partition     | State  | Valid value              | Comment                       |
        ... +===============+========+==========================+===============================+
        ... | S-STATE-01    | TRUE   | True valid value         | State true value              |
        ... +---------------+--------+--------------------------+-------------------------------+
        ... | S-STATE-02    | FALSE  | True valid value         | State false value             |
        ... +---------------+--------+--------------------------+-------------------------------+
        ... 
        ... 
        ... Standard methods
        ... ^^^^^^^^^^^^^^^^^
        ... 
        ... +--------+-------------------------------+
        ... | Method | Comment                       |
        ... +========+===============================+
        ... | toggle | Toggle component state        |
        ... +--------+-------------------------------+
        ... 
        ... \"\"\"
        >>> dt = docutils.core.publish_doctree(matrix)
        >>> state_sections = []
        >>> for section in _filter_section(dt):
        ...     if is_state_section(section):
        ...         state_sections = _filter_list_section(section)
        >>> transition_identification(state_sections)
        {u'State': {u'FALSE': (u'True valid value', u'State false value'), u'TRUE': (u'True valid value', u'State true value')}}
    """
    _clean_children(sections)
    component_transition = []
    for section in sections:
        transitions = {}
        key = _filter_text(_filter_title(section))
        transition_section = get_transition_section(section)
        table = _filter_table(transition_section)
        body = _filter_body(table)
        array_items = []
        row_count = 0
        for row in _filter_row(body):
            row_count += 1
            row_items = []
            content = _filter_paragraph(row)
            for item in content:
                row_items.append(str(_filter_text(item)))
            array_items.append(row_items)

        initial_state = []
        initial_state_id = []
        for i in range(row_count):
            if array_items[i][1] != 'x':
                initial_state_id.append(i)
                if array_items[i][0] == 'x':
                    continue
                interface = getattr(state_module, _to_interface(array_items[i][0]))
                cls = checkmate._utils.get_class_implementing(interface)
                initial_state.append((interface, array_items[i][1]))
                if _is_method(array_items[i][1]):
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(state_module, checkmate._utils.method_basename(array_items[i][1]), functools.partial(cls, checkmate._utils.method_basename(array_items[i][1])))
        for i in range(2, len(array_items[0])):
            input = []
            for j in range(0, initial_state_id[0]):
                interface = getattr(exchange_module, _to_interface(array_items[j][0]))
                input.append((interface, array_items[j][i]))
                if exchange_module is not None:
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(exchange_module, checkmate._utils.method_basename(array_items[j][i]), functools.partial(cls, checkmate._utils.method_basename(array_items[j][i])))
            final = []
            for j in range(initial_state_id[0], initial_state_id[-1]+1):
                if array_items[j][0] == 'x':
                    continue
                interface = getattr(state_module, _to_interface(array_items[j][0]))
                final.append((interface, array_items[j][i]))
                #if state_module is not None:
                #    cls = checkmate._utils.get_class_implementing(interface)
                #    setattr(state_module, checkmate._utils.method_basename(array_items[j][i]), DecFunction)
                #    setattr(state_module, checkmate._utils.method_basename(array_items[j][i]), Decorator(cls, getattr(state_module, checkmate._utils.method_basename(array_items[j][i]))))
            output = []
            for j in range(initial_state_id[-1]+1, row_count):
                interface = getattr(exchange_module, _to_interface(array_items[j][0]))
                output.append((interface, array_items[j][i]))
                if exchange_module is not None:
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(exchange_module, checkmate._utils.method_basename(array_items[j][i]), functools.partial(cls, checkmate._utils.method_basename(array_items[j][i])))
            t = checkmate.transition.Transition(initial=initial_state, incoming=input, final=final, outgoing=output)
            component_transition.append(t)
    return component_transition


def load_partitions(content, _module=None):
    """
    """
    dt = docutils.core.publish_doctree(source=content)
    state_sections = []
    exchange_sections = []
    sm_sections = []
    for section in _filter_section(dt):
        if is_state_section(section):
            state_sections = _filter_list_section(section)
        elif is_exchange_section(section):
            exchange_sections = _filter_list_section(section)

    component_state = partition_identification(state_sections, _module)
    component_exchange = partition_identification(exchange_sections, _module)
    return {'states': component_state, 'exchanges': component_exchange}
    

def load_transitions(content, state_module=None, exchange_module=None):
    """
    """
    dt = docutils.core.publish_doctree(source=content)
    state_sections = []
    exchange_sections = []
    sm_sections = []
    for section in _filter_section(dt):
        if is_state_machine_section(section):
            sm_sections = _filter_list_section(section)

    component_transition = transition_identification(sm_sections, state_module, exchange_module)
    return {'state_machine': component_transition}
    

if __name__ == '__main__':
     _file = file('test/WP7.rst')
     load_partitions(_file.read())
     load_transitions(_file.read())
     _file.close()
