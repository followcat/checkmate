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


def get_signature_arguments(signature, cls):
    """
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import checkmate._exec_tools
        >>> action = sample_app.exchanges.Action
        >>> checkmate._exec_tools.get_signature_arguments("Action('R')", action)
        {}
        >>> checkmate._exec_tools.get_signature_arguments("AP('R2')", action)
        {'R': 'R2'}
    """
    found_label = signature.find('(')
    parameters = signature[found_label:][1:-1].split(', ')
    args = tuple([_p.strip("'") for _p in parameters if (_p != '' and
                  _p.strip("'") not in cls._sig.parameters.keys())])
    arguments = cls._sig.bind_partial(*args).arguments
    return dict(arguments)


def get_exec_signature(signature, exec_module=None, data_structure_module=None):
    """
        >>> import sample_app.application
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_exec_signature("Action(R:ActionRequest)->str", data_structure_module=sample_app.data_structure) #doctest: +ELLIPSIS
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


@checkmate.report_issue('checkmate/issues/exchange_different_data.rst', failed=2)
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
            \n    def __init__(self, value=None, *args, default=True, **kwargs):
            \n        for _k,_v in self.__class__._annotated_values.items():
            \n            if _k not in kwargs or kwargs[_k] is None:
            \n                try:
            \n                    kwargs[_k] = _v(default=default)
            \n                except TypeError:
            \n                    kwargs[_k] = _v()
            \n            else:
            \n                _v = self.__class__._construct_values[_k]
            \n                if not isinstance(kwargs[_k], _v):
            \n                    if isinstance(kwargs[_k], dict):
            \n                        kwargs[_k] = _v(default=default, **kwargs[_k])
            \n                    else:
            \n                        kwargs[_k] = _v(kwargs[_k], default=default)
            \n        super().__init__(value, *args, default=default, **kwargs)
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
        element = class_element('checkmate.interfaces.IExchange', interface_class,
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
        element = class_element('checkmate.interfaces.IState', interface_class,
                                'checkmate.state.State', classname, valid_values_list)
        run_code = get_define_str(element)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    define_interface = getattr(exec_module, interface_class)
    setattr(define_class, '_sig', get_exec_signature(signature, exec_module=exec_module, data_structure_module=data_structure_module))
    exec("_annotated_values = dict([(_k, _v.annotation) for (_k,_v) in _sig.parameters.items()\
           if _v.annotation != inspect._empty])\
         \n_construct_values = dict(_annotated_values)\
         \n_annotated_values.update(dict([(_k, lambda default:_v.default) for (_k, _v) in _sig.parameters.items()\
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
