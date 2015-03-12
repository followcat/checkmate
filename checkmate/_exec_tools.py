# This code is part of the checkmate project.
# Copyright (C) 2014 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os.path
import inspect
import collections

import checkmate._module


def is_method(signature):
    """
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.is_method('item')
        False
        >>> checkmate._exec_tools.is_method('M0()')
        True
    """
    if isinstance(signature, str):
        return '(' in signature
    return False


def method_unbound(signature, interface):
    """
        >>> import checkmate._exec_tools
        >>> import sample_app.application
        >>> import sample_app.component
        >>> interface = sample_app.component.component_3_states.IAcknowledge
        >>> checkmate._exec_tools.method_unbound('func(args)', interface)
        False
        >>> checkmate._exec_tools.method_unbound('append(R)', interface)
        True
        >>> checkmate._exec_tools.method_unbound('append2(R)', interface)
        False
    """
    basename = get_method_basename(signature)
    return is_method(signature) and interface.get(basename) is not None


def get_method_basename(signature):
    """
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_method_basename('Action(R=ActionRequest)')
        'Action'
        >>> checkmate._exec_tools.get_method_basename('func()')
        'func'
        >>> checkmate._exec_tools.get_method_basename('AC.R.r_func()')
        'r_func'
        >>> checkmate._exec_tools.get_method_basename('item')
        'item'
    """
    method = signature.split('(')[0]
    basename = method.split('.')[-1]
    return basename


@checkmate.report_issue('checkmate/issues/function_parameter_exec.rst')
def method_arguments(signature, interface):
    """
        >>> import checkmate._exec_tools
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> interface = sample_app.exchanges.IAction
        >>> checkmate._exec_tools.method_arguments("A0('AT1')", interface)
        ('AT1',)
        >>> checkmate._exec_tools.method_arguments("ActionMix(False, R)", interface)
        ('False',)
        >>> checkmate._exec_tools.method_arguments("AP('R')", interface)
        ()
    """
    args = tuple()
    if is_method(signature):
        cls = checkmate._module.get_class_implementing(interface)
        found_label = signature.find('(')
        parameters = signature[found_label:][1:-1].split(', ')
        args = tuple([_p.strip("'") for _p in parameters if (_p != '' and
                      _p.strip("'") not in cls._sig.parameters.keys())])
    else:
        args = (signature,)
    return args


def get_exec_signature(signature, dependent_modules):
    """
        >>> import sample_app.application
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_exec_signature("Action(R:ActionRequest)->str", [sample_app.data_structure]) #doctest: +ELLIPSIS
        <inspect.Signature object at ...
    """
    exec_dict = {}
    dependent_dict = {}
    method_name = get_method_basename(signature)
    if not is_method(signature):
        signature += '()'
    run_code = """
    \ndef exec_%s:
    \n    pass
    \nfn = exec_%s
        """ % (signature, method_name)
    for _dep in dependent_modules:
        dependent_dict.update(_dep.__dict__)
    exec(run_code, dependent_dict, locals())
    exec(run_code, dependent_dict, locals())
    return inspect.Signature.from_function(locals()['fn'])


@checkmate.report_issue('checkmate/issues/exchange_different_data.rst')
def get_define_str(element):
    run_code = """
            \nimport inspect
            \nimport zope.interface
            \n
            \nimport {i}
            \n
            \nclass {e.interface_class}({e.interface_ancestor_class}):
            \n    \"\"\"\"\"\"
            \n
            \n
            \n@zope.interface.implementer({e.interface_class})
            \nclass {e.classname}({e.ancestor_class}):
            \n    import inspect
            \n    _valid_values = {e.values}
            \n    def __init__(self, value=None, *args, **kwargs):
            \n        for _k,_v in self.__class__._annotated_values.items():
            \n            if _k not in kwargs or kwargs[_k] is None:
            \n                kwargs[_k] = _v()
            \n            else:
            \n                _v = self.__class__._construct_values[_k]
            \n                if not isinstance(kwargs[_k], _v):
            \n                    if isinstance(kwargs[_k], tuple):
            \n                        if isinstance(kwargs[_k][0], tuple):
            \n                            kwargs[_k] = _v(*kwargs[_k][0], **kwargs[_k][1])
            \n                        else:
            \n                            kwargs[_k] = _v(*kwargs[_k])
            \n                    elif isinstance(kwargs[_k], dict):
            \n                        kwargs[_k] = _v(**kwargs[_k])
            \n                    else:
            \n                        kwargs[_k] = _v(kwargs[_k])
            \n        super().__init__(value, *args, **kwargs)
            \n
            """.format(i=os.path.splitext(element.ancestor_class)[0],
                       e=element)

    run_code += """
            \n    @property
            \n    def return_type(self):
            \n        return self._sig.return_annotation
        """
    return run_code


def exec_class_definition(data_structure_module, partition_type, exec_module, signature, codes, values):
    classname = get_method_basename(signature)
    interface_class = 'I' + classname

    class_element = collections.namedtuple('class_element',
                    ['interface_ancestor_class', 'interface_class',
                     'ancestor_class', 'classname', 'values'])
    if partition_type == 'exchanges':
        element = class_element('checkmate.exchange.IExchange', interface_class,
                                'checkmate.exchange.Exchange', classname, values)
        run_code = get_define_str(element)
    elif partition_type == 'data_structure':
        element = class_element('zope.interface.Interface', interface_class,
                                'checkmate.data_structure.DataStructure', classname, values)
        run_code = get_define_str(element)
    elif partition_type == 'states':
        valid_values_list = []
        for _v in values:
            if not is_method(_v):
                valid_values_list.append(_v)
        element = class_element('checkmate.state.IState', interface_class,
                                'checkmate.state.State', classname, valid_values_list)
        run_code = get_define_str(element)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    define_interface = getattr(exec_module, interface_class)
    setattr(define_class, '_sig', get_exec_signature(signature, [data_structure_module, exec_module]))
    exec("_annotated_values = dict([(_k, _v.annotation) for (_k,_v) in _sig.parameters.items()\
           if _v.annotation != inspect._empty])\
         \n_construct_values = dict(_annotated_values)\
         \n_annotated_values.update(dict([(_k, lambda:_v.default) for (_k, _v) in _sig.parameters.items()\
           if _v.annotation != inspect._empty and _v.default != inspect._empty]))\
         \npartition_attribute = tuple([_k for (_k, _v) in _sig.parameters.items()\
           if _v.annotation != inspect._empty])\
         \nclass_attributes = tuple([(_k, _v.default) for (_k, _v) in _sig.parameters.items()\
           if _v.annotation == inspect._empty and _v.default != inspect._empty])",
         dict(define_class.__dict__), globals())
    setattr(define_class, '_annotated_values', globals()['_annotated_values'])
    setattr(define_class, '_construct_values', globals()['_construct_values'])
    setattr(define_class, 'partition_attribute', globals()['partition_attribute'])
    for _k, _v in globals()['class_attributes']:
        setattr(define_class, _k , _v)
    return define_class, define_interface
