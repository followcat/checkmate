# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os.path
import inspect
import collections

import yaml

import checkmate._yaml
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


def get_method_basename(signature):
    """
        >>> import checkmate._exec_tools
        >>> get_basename = checkmate._exec_tools.get_method_basename
        >>> get_basename('Action(R=ActionRequest)')
        'Action'
        >>> get_basename('func()')
        'func'
        >>> get_basename('AC.R.r_func()')
        'r_func'
        >>> get_basename('item')
        'item'
    """
    method = signature.split('(')[0]
    basename = method.split('.')[-1]
    return basename


@checkmate.fix_issue("checkmate/issues/list_signature_arguments.rst")
def get_signature_arguments(signature, cls):
    """
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import checkmate._exec_tools
        >>> action_class = sample_app.exchanges.Action
        >>> arguments = checkmate._exec_tools.get_signature_arguments
        >>> arguments("Action('R')", action_class)
        {'R': 'R'}
        >>> arguments("AP('R2')", action_class)
        {'R': 'R2'}
        >>> checkmate._exec_tools.get_signature_arguments(
        ...     'AP([2, [3, "", null], True, AUTO])', action_class)
        {'R': [2, [3, '', None], True, 'AUTO']}
    """
    found_label = signature.find('(')
    str_args = signature[found_label:][1:-1]
    if len(str_args) == 0:
        return dict()
    args = tuple(yaml.load('[' + str_args + ']',
                            Loader=checkmate._yaml.Loader))
    arguments = cls._sig.bind_partial(*args).arguments
    return dict(arguments)


def get_exec_signature(signature, exec_module=None,
                       data_structure_module=None):
    """
        >>> import sample_app.application
        >>> import checkmate._exec_tools
        >>> signature = checkmate._exec_tools.get_exec_signature
        >>> signature("Action(R:ActionRequest)->str",
        ...     data_structure_module=sample_app.data_structure
        ...     ) #doctest: +ELLIPSIS
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
    if exec_module is not None:
        dependent_dict.update(exec_module.__dict__)
    if data_structure_module is not None:
        dependent_dict.update(data_structure_module.__dict__)
    exec(run_code, dependent_dict, locals())
    return inspect.Signature.from_function(locals()['fn'])


@checkmate.fix_issue("checkmate/issues/builtin_type_no_default.rst")
@checkmate.report_issue('checkmate/issues/exchange_different_data.rst',
    failed=1)
def get_define_str(element):
    run_code = """
\nimport inspect
\n
\nimport {i}
\n
\n
\nclass {e.classname}({e.ancestor_class}):
\n    import inspect
\n    _valid_values = {e.values}
\n    def __init__(self, value=None, *args,
                   default=True, **kwargs):
\n        for _k,_v in self.__class__._construct_values.items():
\n            if self.__class__._sig.parameters[_k].kind == \
                    inspect.Parameter.VAR_POSITIONAL:
\n                if isinstance(kwargs[_k], tuple):
\n                    kwargs[_k] = [_v(item) for item in kwargs[_k]]
\n                else:
\n                    kwargs[_k] = []
\n            elif _k not in kwargs or kwargs[_k] is None:
\n                _v = self.__class__._annotated_values[_k]
\n                try:
\n                    kwargs[_k] = _v(default=default)
\n                except TypeError:
\n                    if default:
\n                        kwargs[_k] = _v()
\n                    else:
\n                        kwargs[_k] = None
\n            elif isinstance(kwargs[_k], dict):
\n                kwargs[_k] = _v(default=default,
                                    **kwargs[_k])
\n            elif not isinstance(kwargs[_k], _v):
\n                kwargs[_k] = _v(kwargs[_k],
                                    default=default)
\n        super().__init__(value, *args, default=default, **kwargs)
\n
            """.format(i=os.path.splitext(element.ancestor_class)[0],
                       e=element)

    run_code += """
\n    @property
\n    def return_type(self):
\n        return self._sig.return_annotation
        """
    for _k, _v in element.attributes.items():
        if type(_v) == str:
            _v = _v.join('""')
        run_code += """
\n    {key} = {value}
            """.format(key=_k, value=_v)
    return run_code


def exec_class_definition(data_structure_module, partition_type, exec_module,
                          signature, values, attributes):
    """"""
    classname = get_method_basename(signature)
    class_element = collections.namedtuple('class_element',
                    ['ancestor_class', 'classname', 'values', 'attributes'])
    if partition_type == 'exchanges':
        element = class_element(
                    'checkmate.exchange.Exchange',
                    classname,
                    values,
                    attributes)
        run_code = get_define_str(element)
    elif partition_type == 'data_structure':
        element = class_element(
                    'checkmate.data_structure.DataStructure',
                    classname,
                    values,
                    attributes)
        run_code = get_define_str(element)
    elif partition_type == 'states':
        valid_values_list = []
        for _v in values:
            if not is_method(_v):
                valid_values_list.append(_v)
        element = class_element(
                    'checkmate.state.State',
                    classname,
                    valid_values_list,
                    attributes)
        run_code = get_define_str(element)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    setattr(define_class, '_sig',
        get_exec_signature(signature, exec_module=exec_module,
            data_structure_module=data_structure_module))
    exec("""_annotated_values = dict([(_k, _v.annotation)
                                    for (_k,_v) in _sig.parameters.items()
                                    if _v.annotation != inspect._empty])
         \n_construct_values = dict(_annotated_values)
         \n_annotated_values.update(
                dict([(_k, lambda default:_v.default)
                      for (_k, _v) in _sig.parameters.items()
                      if (_v.annotation != inspect._empty and
                          _v.default != inspect._empty)]))
         \npartition_attribute = \
                tuple([_k for (_k, _v) in _sig.parameters.items()
                       if _v.annotation != inspect._empty])""",
         dict(define_class.__dict__), globals())
    setattr(define_class, '_annotated_values',
        globals()['_annotated_values'])
    setattr(define_class, '_construct_values',
        globals()['_construct_values'])
    setattr(define_class, 'partition_attribute',
        globals()['partition_attribute'])
    return define_class
