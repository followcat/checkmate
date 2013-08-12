import ast
import sys

import zope.interface


def _has_argument(signature):
    if signature == '':
        return False
    body = ast.parse(signature).body[0]
    try:
        return (len(body.value.keywords) >= 0 or
                len(body.value.args) >= 0)
    except AttributeError:
        return False

def _leading_name(signature):
    """
        >>> _leading_name('Action(R=ActionRequest)')
        'Action'
    """
    body = ast.parse(signature).body[0]
    try:
        return body.value.func.attr
    except AttributeError:
        return body.value.func.id

def _arguments(signature):
    """
        >>> _arguments('func(a)')
        ['a']
        >>> _arguments("func('a')")
        ['a']
        >>> _arguments('f()')
        []
    """
    output = []
    body = ast.parse(signature).body[0]
    try:
        for a in body.value.args:
            if type(a) == ast.Name:
                output.append(a.id)
            elif type(a) == ast.Str:
                output.append(a.s)
    finally:
        return output

def _kw_arguments(signature):
    """
        >>> _kw_arguments('func(a)')
        []
        >>> _kw_arguments("func('a')")
        []
        >>> _kw_arguments('f(a=b)')
        [('a', 'b')]
        >>> _kw_arguments('RQ(R(HIGH))')
        [('R', 'HIGH')]
        >>> _kw_arguments("RQ(R('HIGH'))")
        [('R', 'HIGH')]
        >>> _kw_arguments("RQ(R(P='HIGH', A='AT1'))")
        [('R', "R(P='HIGH', A='AT1')")]
    """
    output = []
    body = ast.parse(signature).body[0]
    try:
        #format the first layer of signature arguments
        for a in body.value.keywords:
            if type(a.value) == ast.Name:
                output.append((a.arg, a.value.id))
            elif type(a.value) == ast.Str:
                output.append((a.arg, a.value.s))
        _arg = body.value.args[0]
        if hasattr(_arg, 'args') and len(_arg.args) > 0:
            for arg in _arg.args:
                if type(arg) == ast.Name:
                    output.append((_arg.func.id, arg.id))
                elif type(arg) == ast.Str:
                    output.append((_arg.func.id, arg.s))
        #keep the internal layers of signature arguments
        if hasattr(_arg, 'keywords') and len(_arg.keywords) > 0:
            _s = signature
            _output = _s[_s.index(_arg.func.id+'('):_s.rindex(')')]
            output.append((_arg.func.id, _output))
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
        >>> is_method('M0()')
        True
        >>> is_method('Q(R=NORM)')
        True
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
        >>> valid_value_argument("A0('AT1')")
        'AT1'
    """
    if is_method(signature):
        if (len(_arguments(signature)) == 1):
            return _arguments(signature)[0]
    return None

def method_arguments(signature):
    """
        >>> method_arguments('func(AUTO, HIGH)')
        (('AUTO', 'HIGH'), {})
        >>> method_arguments("A0('AT1')")
        (('AT1',), {})

        >>> method_arguments('M0(True)')
        (('True',), {})
        >>> method_arguments("A0('AT1')")
        (('AT1',), {})
        >>> method_arguments('Q(None)')
        (('None',), {})
        >>> l,d = method_arguments('func(R, P=HIGH)')
        >>> len (l)
        0
        >>> d['P'].values[0]
        'HIGH'
        >>> method_arguments('Action(R=ActionRequest)')
        ((), {'R': (('ActionRequest',), {})})
        >>> method_arguments('RQ(R(HIGH))')
        ((), {'R': (('HIGH',), {})})
        >>> output = method_arguments('ActionRequest(P=ActionPriority, A=Attribute)')
        >>> (output[-1]['P'].values[0], output[-1]['A'].values[0])
        ('ActionPriority', 'Attribute')
        >>> method_arguments('RQ(R(P=HIGH))') 
        ((), {'R': ((), {'P': (('HIGH',), {})})})
        >>> o = method_arguments("RQ(R(P='HIGH', A='AT1'))")
        >>> o.attribute_values['R'].attribute_values['A'].values
        ('AT1',)
        >>> o.attribute_values['R'].attribute_values['P'].values
        ('HIGH',)
    """
    _args = []
    _kw_args = {}
    if is_method(signature):
        for argument in _arguments(signature):
            if argument_value(argument):
                _args.append(argument)
            else:
                _kw_args[argument] = None
        for item in _kw_arguments(signature):
            _kw_val = item[1]
            if is_method(item[1]):
                # get inside layer of argument
                _kw_val = method_arguments(item[1])
            else:
                # format the value
                _kw_val = ArgumentStorage((tuple((item[1],)), {}))
            _kw_args[item[0]] = _kw_val
    return ArgumentStorage((tuple(_args), _kw_args))

def argument_value(argument):
    """
    """
    return (argument.isdigit() or
        argument in ['True', 'False', 'AT1', 'AT2', 'NORM', 'HIGH', 'None', 'AUTO', 'MANUAL'])

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

class IArgumentStorage(zope.interface.Interface):
    """"""

@zope.interface.implementer(IArgumentStorage)
class ArgumentStorage(tuple):
    """"""
    @property
    def values(self):
        assert (len(self) == 2)
        return self[0]

    @property
    def attribute_values(self):
        assert (len(self) == 2)
        return self[1]

