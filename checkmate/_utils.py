import re
import sys


ARGUMENT = re.compile('(.*?)\((.*)\)')


def _has_argument(name):
    return (ARGUMENT.search(name) is not None)

def _leading_name(signature):
    return ARGUMENT.search(signature).group(1)

def _arguments(signature):
    """
        >>> _arguments("func('a')")
        'a'
        >>> _arguments('func(a)')
        'a'
        >>> _arguments('f()')
        ''
    """
    args = ARGUMENT.search(signature).group(2).split(',')
    return_str = []
    if args is not None and len(args) != 0:
        for arg in args:
            return_str.append(arg.rstrip('\'"'). lstrip('\'"'))
    return ','.join(return_str)

def _method_basename(signature):
    """
        >>> _method_basename('func(arg=value)')
        'func'
        >>> _method_basename('self.func()')
        'func'
    """
    if is_method(signature):
        return _leading_name(signature).split('.')[-1]


def internal_code(value):
    """
        >>> internal_code('func(args)')
        'func'
        >>> signature = 'item'
        >>> internal_code(signature)
        'item'
    """
    output = _method_basename(value)
    if output == None:
        return value
    return output

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
            '.' in _leading_name(signature))

def valid_value_argument(signature):
    """ All input signatures have value as argument (from state partitions)

        >>> valid_value_argument('M0(MANUAL)')
        'MANUAL'
    """
    if is_method(signature):
        if (len(_arguments(signature)) != 0 and
            ',' not in _arguments(signature)):
            argument = _arguments(signature)
            return argument
    return None

def method_value_arguments(signature):
    """ All arguments are value

        >>> method_value_arguments('func(AUTO, HIGH)')
        (['AUTO', ' HIGH'], {})
    """
    _args = []
    if is_method(signature):
        if len(_arguments(signature)) != 0:
            for argument in _arguments(signature).split(','):
                _args.append(argument)
    return (_args, {})

def method_arguments(signature):
    """
        >>> method_arguments('M0(True)')
        (['True'], {})
    """
    _args = []
    _kw_args = {}
    if is_method(signature):
        if len(_arguments(signature)) != 0:
            for argument in _arguments(signature).split(','):
                if argument_value(argument):
                    _args.append(argument.rstrip('\'"').lstrip('\'"'))
                else:
                    if _has_argument(argument):
                        _kw_args[_leading_name(argument)] = _arguments(argument)
                    else:
                        _kw_args[argument] = None
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

