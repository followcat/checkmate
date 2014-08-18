import re
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
    return '(' in signature


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


def get_parameters_list(parameter_str):
    """

        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_parameters_list("'AT1'")
        ['AT1']
        >>> checkmate._exec_tools.get_parameters_list("R = ActionRequest(['AT2', 'HIGH']), R = ['HIGH']")
        ["R = ActionRequest(['AT2', 'HIGH'])", "R = ['HIGH']"]
    """
    temp_list = []
    temp_str = ''
    bracket_count = 0
    for _s in parameter_str.split(','):
        if _s == '':
            continue
        bracket_count += _s.count('(')
        bracket_count -= _s.count(')')
        temp_str += _s
        if bracket_count == 0:
            temp_list.append(temp_str.strip(' \'"'))
            temp_str = ''
            continue
        temp_str += ','
    return temp_list


def get_function_parameters_list(signature):
    """
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_function_parameters_list("A0('AT1')")
        ['AT1']
        >>> checkmate._exec_tools.get_function_parameters_list("Action(R = ActionRequest(['AT2', 'HIGH']))")
        ["R = ActionRequest(['AT2', 'HIGH'])"]
    """
    found_label = signature.find('(')
    parameter_str = signature[found_label:][1:-1]
    return get_parameters_list(parameter_str)


def get_exec_signature(signature, dependent_module):
    """
        >>> import sample_app.application
        >>> import checkmate._exec_tools
        >>> exec_sig = checkmate._exec_tools.get_exec_signature("Action(R:ActionRequest)->str", sample_app.data_structure)
        >>> exec_sig['_sig'] # doctest: +ELLIPSIS
        <inspect.Signature object at ...
    """
    exec_dict = {}
    method_name = get_method_basename(signature)
    if not is_method(signature):
        signature += '()'
    run_code = """
    \ndef exec_%s:
    \n    pass
    \nfn = exec_%s
        """ % (signature, method_name)
    exec(run_code, dependent_module.__dict__, locals())
    exec_dict = dict((['_sig', inspect.Signature.from_function(locals()['fn'])], ))
    return exec_dict


def method_arguments(signature, interface):
    """
        >>> import checkmate._exec_tools
        >>> import sample_app.application
        >>> interface = sample_app.exchanges.IAction
        >>> argument = checkmate._exec_tools.method_arguments("ActionMix(False, R = None)", interface)
        >>> argument['attribute_values'], argument['values']
        ({'R': None}, ('False',))
        >>> argument = checkmate._exec_tools.method_arguments("AP('R')", interface)
        >>> argument['attribute_values'], argument['values']
        ({'R': None}, ())
    """
    args = []
    kwargs = {}
    cls = checkmate._module.get_class_implementing(interface)
    argument = {'values': None, 'attribute_values': kwargs}
    if is_method(signature):
        parameters_list = get_function_parameters_list(signature)
    else:
        parameters_list = get_parameters_list(signature)
    for each in parameters_list:
        if '=' not in each:
            if each in cls.__init__.__annotations__.keys():
                kwargs[each] = None
            else:
                args.append(each)
        else:
            label = each.find('=')
            _k, _v = each[:label].strip(), each[label + 1:].strip()
            exec("kwargs['%s'] = %s" % (_k, _v))
    argument['values'] = tuple(args)
    return argument


def get_exchange_define_str(import_module, interface_class, classname, parameters_str, annotations_str, annotations_list, codes):
    parameters_keys = re.compile(r'=[\w]+').sub('', parameters_str)
    class_element = collections.namedtuple('class_element', ['import_module', 'interface_class', 'classname', 'parameters_str', 'parameters_keys', 'annotations_str'])
    element = class_element(import_module, interface_class, classname, parameters_str, parameters_keys, annotations_str)
    run_code = """
            \nimport inspect
            \nimport zope.interface
            \n
            \nimport checkmate.exchange
            \n{e.import_module}
            \n
            \nclass {e.interface_class}(checkmate.exchange.IExchange):
            \n    \"\"\"\"\"\"
            \n
            \n
            \n@zope.interface.implementer({e.interface_class})
            \nclass {e.classname}(checkmate.exchange.Exchange):
            \n    def __init__(self, value=None, *args, **kwargs):
            \n        partition_attribute = []
            \n        for _k,_v in self._sig.parameters.items():
            \n            if _v.annotation == inspect._empty:
            \n                continue
            \n            if _k in kwargs:
            \n                setattr(self, _k, kwargs[_k])
            \n                kwargs.pop(_k)
            \n            elif hasattr(_v, 'annotation'):
            \n                setattr(self, _k, _v.annotation())
            \n            partition_attribute.append(_k)
            \n        super().__init__(value, *args, **kwargs)
            \n        self.partition_attribute = tuple(partition_attribute)
            \n
            """.format(e=element)

    class_action = collections.namedtuple('class_action', ['classname', 'code'])
    for _c in codes[0]:
        internal_code = get_method_basename(_c)
        action = class_action(classname, internal_code)
        run_code += """
        \ndef {a.code}(*args, **kwargs):
        \n    return {a.classname}('{a.code}', *args, **kwargs)
        """.format(a=action)
    return run_code


def get_data_structure_define_str(interface_class, classname, valid_values_list):
    class_element = collections.namedtuple('class_element', ['interface_class', 'classname', 'valid_values'])
    element = class_element(interface_class, classname, valid_values_list)
    run_code = """
        \nimport zope.interface
        \n
        \nclass {e.interface_class}(zope.interface.Interface):
        \n    \"\"\"\"\"\"
        \n
        \n
        \n@zope.interface.implementer({e.interface_class})
        \nclass {e.classname}(list):
        \n    _valid_values = {e.valid_values}
        \n    def __init__(self, *args):
        \n        for _l in self._valid_values:
        \n            for _argv in args:
        \n                if _argv in _l:
        \n                    self.append(_argv)
        \n                    break
        \n            else:
        \n                self.append(_l[0])
        """.format(e=element)
    return run_code


def get_states_define_str(interface_class, classname, valid_values_list):
    class_element = collections.namedtuple('class_element', ['interface_class', 'classname', 'valid_values'])
    element = class_element(interface_class, classname, valid_values_list)
    run_code = """
        \nimport zope.interface
        \n
        \nimport checkmate.state
        \n
        \n
        \nclass {e.interface_class}(checkmate.state.IState):
        \n    \"\"\"\"\"\"
        \n
        \n
        \n@zope.interface.implementer({e.interface_class})
        \nclass {e.classname}(checkmate.state.State):
        \n    _valid_values = {e.valid_values}
        \n    def __init__(self, *args, **kwargs):
        \n        super().__init__(*args, **kwargs)
        """.format(e=element)
    return run_code


def exec_class_definition(data_structure_module, partition_type, exec_module, signature, codes):
    classname = get_method_basename(signature)
    interface_class = 'I' + classname

    if partition_type == 'exchanges':
        import_module = ''
        annotations_str = ''
        annotations_list = []
        parameters_str = ''
        for _p in get_function_parameters_list(signature):
            if ':' in _p:
                temp_p = _p.replace(':', ':' + data_structure_module.__name__ + '.')
                annotations_list.append(temp_p)
                annotations_str += ', ' + temp_p + '=None'
            else:
                parameters_str += ', ' + _p
        if annotations_list:
            import_module = "import " + data_structure_module.__name__
        run_code = get_exchange_define_str(import_module, interface_class, classname, parameters_str, annotations_str, annotations_list, codes)

    elif partition_type == 'data_structure':
        run_code = get_data_structure_define_str(interface_class, classname, codes)

    elif partition_type == 'states':
        valid_values_list = []
        for _c in codes[0]:
            if is_method(_c):
                valid_values_list.extend(get_function_parameters_list(_c))
            else:
                valid_values_list.extend(get_parameters_list(_c))
        run_code = get_states_define_str(interface_class, classname, valid_values_list)

    sig_dict = get_exec_signature(signature, data_structure_module)
    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    setattr(define_class, '_sig', sig_dict['_sig'])
    define_interface = getattr(exec_module, interface_class)
    return define_class, define_interface
