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


def get_function_name(signature):
    """
        >>> get_function_name('Action(R:ActionRequest)')
        'Action'
    """
    return signature.split('(')[0]


def get_function_parameters_list(signature):
    """
        >>> get_function_parameters_list('ActionRequest(P:ActionPriority, A:Attribute)')
        ['P:ActionPriority', 'A:Attribute']
    """
    found_label = signature.find('(')
    if found_label == -1:
        return ''
    temp_list = [_p.strip(' \'"') for _p in signature[signature.find('('):][1:-1].split(',')]
    return temp_list
