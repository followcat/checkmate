import re
import sys


def internal_code(value):
    output = method_basename(value)
    if output == None:
        return value
    return output

def is_method(name):
    return (re.compile('\(.*\)').search(name) is not None)

def method_unbound(signature):
    """"""
    return ('(' in signature and
            '.' in signature[:signature.index('(')])

def method_basename(signature):
    """
    """
    if '(' in signature:
        return signature[:signature.index('(')].split(u'.')[-1]

def valid_value_argument(signature):
    if '(' in signature:
        if (signature.index('(') != signature.index(')')-1 and
            ',' not in signature[signature.index('(')+1:signature.index(')')]):
            argument = signature[signature.index('(')+1:signature.index(')')]
            if argument_value(argument):
                return argument
    return None

def method_value_arguments(signature):
    """ All arguments are value """
    _args = []
    if '(' in signature:
        if (signature.index('(') != signature.index(')')-1):
            for argument in signature[signature.index('(')+1:signature.index(')')].split(','):
                _args.append(argument)
    return (_args, {})

def method_arguments(signature):
    _args = []
    _kw_args = {}
    if '(' in signature:
        if (signature.index('(') != signature.index(')')-1):
            for argument in signature[signature.index('(')+1:signature.index(')')].split(','):
                if argument_value(argument):
                    _args.append(argument)
                else:
                    _kw_args[argument] = None
    return (_args, _kw_args)

def argument_value(argument):
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
    for _o in module.__dict__.values():
        if inspect.isclass(_o):
            if interface.implementedBy(_o):
                return _o
