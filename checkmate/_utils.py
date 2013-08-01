import ast
import sys


def _has_argument(signature):
    body = ast.parse(signature).body[0]
    try:
        return (len(body.value.keywords) > 0 or
                len(body.value.args) > 0)
    except AttributeError:
        return False

def _leading_name(signature):
    body = ast.parse(signature).body[0]
    try:
        return body.value.func.attr
    except AttributeError:
        return body.value.func.id

def _arguments(signature):
    """
        >>> _arguments('func(a)')
        'a'
        >>> _arguments('f()')
        ''
    """
    output = []
    body = ast.parse(signature).body[0]
    try:
        for a in body.value.args:
            output.append(a.id)
    finally:
        return output

def _kw_arguments(signature):
    """
        >>> _kw_arguments('func(a)')
        []
        >>> _kw_arguments('f(a=b)')
        [('a', 'b')]
    """
    output = []
    body = ast.parse(signature).body[0]
    try:
        for a in body.value.keywords:
            output.append((a.arg, a.value.id))
    finally:
        return output

def _method_basename(signature):
    """
        >>> _method_basename('func(arg=value)')
        'func'
        >>> _method_basename('self.func()')
        'func'
    """
    body = ast.parse(signature).body[0]
    try:
        return body.value.func.attr
    except AttributeError:
        return body.value.func.id


def internal_code(value):
    """
        >>> internal_code('func(args)')
        'func'
        >>> signature = 'item'
        >>> internal_code(signature)
        'item'
    """
    try:
        output = _method_basename(value)
        return output
    except:
        return value

def is_method(name):
    """
        >>> is_method('item')
        False
        >>> is_method('M0("AUTO")')
        True
    """
    return _has_argument(name)

def method_unbound(signature):
    """
        >>> method_unbound('func(args)')
        False
        >>> method_unbound('Q0.append(R)')
        True
    """
    return (is_method(signature) and
            '.' in signature)

def valid_value_argument(signature):
    """ All input signatures have value as argument (from state partitions)

        >>> valid_value_argument('M0(MANUAL)')
        'MANUAL'
    """
    if is_method(signature):
        if (len(_arguments(signature)) == 1):
            return _arguments(signature)[0]
    return None

def method_value_arguments(signature):
    """ All arguments are value

        >>> method_value_arguments('func(AUTO, HIGH)')
        (['AUTO', 'HIGH'], {})
    """
    _args = []
    if is_method(signature):
        if len(_arguments(signature)) != 0:
            for argument in _arguments(signature):
                _args.append(argument)
    return (_args, {})

def method_arguments(signature):
    """
        >>> method_arguments('M0(True)')
        (['True'], {})
        >>> method_arguments('func(R, P=HIGH)')
        ([], {'R': None, 'P': 'HIGH'})
    """
    _args = []
    _kw_args = {}
    if is_method(signature):
        for argument in _arguments(signature):
            if argument_value(argument):
                _args.append(argument.rstrip('\'"'). lstrip('\'"'))
            else:
                _kw_args[argument] = None
        for item in _kw_arguments(signature):
            _kw_args[item[0]] = item[1]
    return (_args, _kw_args)

def argument_value(argument):
    """
    """
    return ("'" in argument or '"' in argument or
        argument.isdigit() or
        argument in ['True', 'False'])

def get_module_defining(interface):
    module_name = interface.__module__
    module = None
    try:
        module = sys.modules[module_name]

    except KeyError:
        path = None
        for x in module_name.split('.'):
            fp, pathname, description = imp.find_module(x, path)
            path = [pathname]
        module = imp.load_module(module_name, fp, pathname, description)
        pass
    return module

def get_class_implementing(interface):
    """"""
    import imp
    import inspect

    module = get_module_defining(interface)
    for _o in list(module.__dict__.values()):
        if inspect.isclass(_o):
            if interface.implementedBy(_o):
                return _o

