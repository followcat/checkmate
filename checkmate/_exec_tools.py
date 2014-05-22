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


def get_function_name(signature):
    """
        >>> get_function_name('Action(R:ActionRequest)')
        'Action'
    """
    return signature.split('(')[0]


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


def method_arguments(signature):
    """
        >>> argument = method_arguments("ActionMix(False, R = None)")
        >>> argument['attribute_values'], argument['values']
        ({'R': None}, ('False',))
    """
    args = []
    kwargs = {}
    argument = {'values': None, 'attribute_values': kwargs}
    for each in get_function_parameters_list(signature):
        if '=' not in each:
            exec("args.append('%s')" % (each))
        else:
            equre_label = each.find('=')
            _k, _v = each[:equre_label].strip(), each[equre_label + 1:].strip()
            exec("kwargs['%s'] = %s" % (_k, _v))
    argument['values'] = tuple(args)
    return argument
