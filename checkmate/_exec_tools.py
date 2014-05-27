import checkmate._module


def is_method(signature):
    """
        >>> is_method('item')
        False
        >>> is_method('M0()')
        True
        >>> is_method('Q(R=NORM)')
        True
        >>> is_method('M0("AUTO")')
        True
    """
    if len(signature.split('(')) == 1:
        return False
    return True


def method_unbound(signature):
    """
        >>> method_unbound('func(args)')
        False
        >>> method_unbound('Q0.append(R)')
        True
    """
    return (is_method(signature) and
            '.' in signature)


def get_method_basename(signature):
    """
        >>> get_method_basename('Action(R=ActionRequest)')
        'Action'
        >>> get_method_basename('self.func()')
        'func'
        >>> get_method_basename('self.AC.R.r_func()')
        'r_func'
        >>> get_method_basename('item')
        'item'
    """
    method = signature.split('(')[0]
    basename = method.split('.')[-1]
    return basename


def get_function_parameters_list(signature):
    """
        >>> get_function_parameters_list("A0('AT1')")
        ['AT1']
        >>> get_function_parameters_list("ActionMix(AR(P = AP('HIGH', 'NORM', 'LOW')), R = AR(P = AP('HIGH', 'NORM'), A = A()), K = None, Value = 5)")
        ["AR(P = AP('HIGH', 'NORM', 'LOW'))", "R = AR(P = AP('HIGH', 'NORM'), A = A())", 'K = None', 'Value = 5']
    """
    temp_list = []
    found_label = signature.find('(')
    if found_label == -1 or len(signature[found_label:][1:-1]) == 0:
        return temp_list
    temp_str = ''
    left_count = 0
    for _s in signature[found_label:][1:-1].split(','):
        left_count += _s.count('(')
        left_count -= _s.count(')')
        temp_str += _s
        if left_count == 0:
            temp_list.append(temp_str.strip(' \'"'))
            temp_str = ''
            continue
        temp_str += ','
    return temp_list


def method_arguments(signature, interface):
    """
        >>> import sample_app.application
        >>> interface = sample_app.exchanges.IAction
        >>> argument = method_arguments("ActionMix(False, R = None)", interface)
        >>> argument['attribute_values'], argument['values']
        ({'R': None}, ('False',))
        >>> argument = method_arguments("AP('R')", interface)
        >>> argument['attribute_values'], argument['values']
        ({'R': None}, ())
    """
    args = []
    kwargs = {}
    cls = checkmate._module.get_class_implementing(interface)
    argument = {'values': None, 'attribute_values': kwargs}
    for each in get_function_parameters_list(signature):
        if '=' not in each:
            if each in cls.__init__.__annotations__.keys():
                kwargs[each] = None
            else:
                args.append(each)
        else:
            equre_label = each.find('=')
            _k, _v = each[:equre_label].strip(), each[equre_label + 1:].strip()
            exec("kwargs['%s'] = %s" % (_k, _v))
    argument['values'] = tuple(args)
    return argument
