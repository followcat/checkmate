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
    if is_method(signature) and interface.get(basename):
        return True
    else:
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


def get_parameters_list(parameter_str):
    """
        >>> import checkmate._exec_tools
        >>> checkmate._exec_tools.get_parameters_list("'AT1'")
        ['AT1']
        >>> checkmate._exec_tools.get_parameters_list("AR(P = AP('HIGH', 'NORM', 'LOW')), R = AR(P = AP('HIGH', 'NORM'), A = A()), K = None, Value = 5")
        ["AR(P = AP('HIGH', 'NORM', 'LOW'))", "R = AR(P = AP('HIGH', 'NORM'), A = A())", 'K = None', 'Value = 5']
    """
    temp_list = []
    temp_str = ''
    left_count = 0
    for _s in parameter_str.split(','):
        left_count += _s.count('(')
        left_count -= _s.count(')')
        temp_str += _s
        if left_count == 0:
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
        >>> checkmate._exec_tools.get_function_parameters_list("ActionMix(AR(P = AP('HIGH', 'NORM', 'LOW')), R = AR(P = AP('HIGH', 'NORM'), A = A()), K = None, Value = 5)")
        ["AR(P = AP('HIGH', 'NORM', 'LOW'))", "R = AR(P = AP('HIGH', 'NORM'), A = A())", 'K = None', 'Value = 5']
    """
    temp_list = []
    found_label = signature.find('(')
    if found_label == -1 or len(signature[found_label:][1:-1]) == 0:
        return temp_list
    parameter_str = signature[found_label:][1:-1]
    return get_parameters_list(parameter_str)


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
