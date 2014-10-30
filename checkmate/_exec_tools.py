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


@checkmate.report_issue('checkmate/issues/function_parameter_exec.rst')
def method_arguments(signature, interface):
    """
        >>> import checkmate._exec_tools
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> interface = sample_app.exchanges.IAction
        >>> checkmate._exec_tools.method_arguments("A0('AT1')", interface)
        (('AT1',), {})

        >>> checkmate._exec_tools.method_arguments("ActionMix(False, R = None)", interface)
        (('False',), {'R': None})
        >>> checkmate._exec_tools.method_arguments("AP('R')", interface)
        ((), {'R': None})
    """
    if is_method(signature):
        found_label = signature.find('(')
        parameter_str = signature[found_label:][1:-1]
        parameters = get_parameters_list(parameter_str)
    else:
        parameters = get_parameters_list(signature)

    args = []
    kwargs = {}
    cls = checkmate._module.get_class_implementing(interface)
    for each in parameters:
        if '=' not in each:
            if each in cls._sig.parameters.keys():
                kwargs[each] = None
            else:
                args.append(each)
        else:
            label = each.find('=')
            _k, _v = each[:label].strip(), each[label + 1:].strip()
            exec("kwargs['%s'] = %s" % (_k, _v), locals(), locals())
    return tuple(args), kwargs


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


def get_exchange_define_str(interface_class, classname, codes, values):
    class_element = collections.namedtuple('class_element', ['interface_class', 'classname', 'codes', 'values'])
    internal_codes = [get_method_basename(_c) for _c in codes]
    element = class_element(interface_class, classname, internal_codes, values)
    run_code = """
            \nimport inspect
            \nimport zope.interface
            \n
            \nimport checkmate.exchange
            \n
            \nclass {e.interface_class}(checkmate.exchange.IExchange):
            \n    \"\"\"\"\"\"
            \n
            \n
            \n@zope.interface.implementer({e.interface_class})
            \nclass {e.classname}(checkmate.exchange.Exchange):
            \n    _valid_values = {e.values}
            \n    _codes = {e.codes}
            \n    def __init__(self, value=None, *args, **kwargs):
            \n        partition_attribute = []
            \n        for _k,_v in self._sig.parameters.items():
            \n            if _k not in kwargs or kwargs[_k] is None:
            \n                if _v.annotation == inspect._empty:
            \n                    kwargs[_k] = _v.default
            \n                else:
            \n                    kwargs[_k] = _v.annotation()
            \n                    partition_attribute.append(_k)
            \n        bound = self._sig.bind(*args, **kwargs)
            \n        super().__init__(value, **bound.arguments)
            \n        self.partition_attribute = tuple(partition_attribute)
            \n
            """.format(e=element)

    for _c, _v in zip(internal_codes, values):
        sep = ''
        if type(_v) == str:
            sep = "'"
        run_code += """
        \ndef {code}(*args, **kwargs):
        \n    return {cls}({sep}{value}{sep}, *args, **kwargs)
        """.format(cls=classname, code=_c, sep=sep, value=_v)
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


def exec_class_definition(data_structure_module, partition_type, exec_module, signature, codes, values):
    classname = get_method_basename(signature)
    interface_class = 'I' + classname

    if partition_type == 'exchanges':
        run_code = get_exchange_define_str(interface_class, classname, codes, values)
    elif partition_type == 'data_structure':
        run_code = get_data_structure_define_str(interface_class, classname, values)
    elif partition_type == 'states':
        valid_values_list = []
        for _v in values:
            if not is_method(_v):
                valid_values_list.append(_v)
        run_code = get_states_define_str(interface_class, classname, valid_values_list)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    setattr(define_class, '_sig', get_exec_signature(signature, [data_structure_module]))
    define_interface = getattr(exec_module, interface_class)
    return define_class, define_interface
