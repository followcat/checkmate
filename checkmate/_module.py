import os
import imp
import sys
import inspect
import importlib
import collections

import checkmate._exec_tools


def get_exchange_define_str(import_module, interface_class, classname, parameters_str, parameters_list, codes):
    class_element = collections.namedtuple('class_element', ['import_module', 'interface_class', 'classname', 'parameters_str'])
    element = class_element(import_module, interface_class, classname, parameters_str)
    run_code = """
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
            \n    def __init__(self, value=None, *args{e.parameters_str}, **kwargs):
            \n        super().__init__(value)
            \n        self.partition_attribute = tuple({e.classname}.__init__.__annotations__.keys())
            \n
            """.format(e=element)

    class_parame = collections.namedtuple('class_parame', ['attribute', 'classname'])
    for _p in parameters_list:
        _k, _v = _p.split(':')
        parame = class_parame(_k, _v)
        run_code += """
            \n        if {p.attribute} is None:
            \n            self.{p.attribute} = {p.classname}(*args)
            \n        else:
            \n            self.{p.attribute} = {p.attribute}
            """.format(p=parame)

    class_action = collections.namedtuple('class_action', ['classname', 'code'])
    for _c in codes[0]:
        internal_code = checkmate._exec_tools.get_method_basename(_c)
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
    classname = checkmate._exec_tools.get_method_basename(signature)
    interface_class = 'I' + classname

    if partition_type == 'exchanges':
        import_module = ''
        parameters_str = ''
        parameters_list = checkmate._exec_tools.get_function_parameters_list(signature)
        if len(parameters_list) > 0:
            import_module = "import " + data_structure_module.__name__
            parameters_list = [_p.replace(':', ':' + data_structure_module.__name__ + '.') for _p in parameters_list]
            parameters_str = ', ' + ', '.join([_p + '=None' for _p in parameters_list])
        run_code = get_exchange_define_str(import_module, interface_class, classname, parameters_str, parameters_list, codes)

    elif partition_type == 'data_structure':
        run_code = get_data_structure_define_str(interface_class, classname, codes)

    elif partition_type == 'states':
        valid_values_list = []
        for _c in codes[0]:
            if checkmate._exec_tools.is_method(_c):
                valid_values_list.extend(checkmate._exec_tools.get_function_parameters_list(_c))
            else:
                valid_values_list.extend(checkmate._exec_tools.get_parameters_list(_c))
        run_code = get_states_define_str(interface_class, classname, valid_values_list)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    define_interface = getattr(exec_module, interface_class)
    return define_class, define_interface


def get_module(package_name, module_name, alternative_package=None):
    """Load existing module or create a new one

    The provided package_name is expected to be a sub-package
    under the project main package (eg. 'main.sub').

    This function can be used to create a module in an alternative package beside the provided one:
        >>> import checkmate._module
        >>> import sample_app.application
        >>> mod = checkmate._module.get_module('sample_app.application', 'xxx', 'component')
        >>> mod # doctest: +ELLIPSIS
        <module 'sample_app.component.xxx' from ...

    It can also be used to create a new module beside an existing one in the provided package:
        >>> mod2 = checkmate._module.get_module('sample_app.component.xxx', 'yyy')
        >>> mod2 # doctest: +ELLIPSIS
        <module 'sample_app.component.yyy' from ...

        >>> mod3 = checkmate._module.get_module('checkmate.application', 'data')
        >>> mod3 # doctest: +ELLIPSIS
        <module 'checkmate.data' from ...
    """
    assert(len(package_name.split('.')) > 1)

    basename = package_name.split('.')[-1]
    _file = sys.modules[package_name].__file__

    if alternative_package is None:
        if len(package_name.split('.')) > 2:
            alternative_package = '.' + package_name.split('.')[-2]
        else:
            alternative_package = package_name.split('.')[-2]
        _fullname = alternative_package + '.' + basename
        _new_fullname = alternative_package + '.' + module_name
    else:
        _fullname = '.' + basename
        alternative_package = '.' + alternative_package
        _new_fullname = alternative_package + '.' + module_name
    _name = package_name.replace(_fullname, _new_fullname)

    if _name in sys.modules:
        module = sys.modules[_name]
    else:
        module = imp.new_module(_name)
        module.__name__ = _name
        module.__file__ = _file.replace(_fullname.replace('.', os.sep), _new_fullname.replace('.', os.sep))
        sys.modules[_name] = module
        setattr(importlib.import_module(package_name.replace(_fullname, alternative_package), package_name.replace(_fullname, '')), module_name, module)
    return module


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
    module = get_module_defining(interface)
    for _o in list(module.__dict__.values()):
        if inspect.isclass(_o):
            if interface.implementedBy(_o):
                return _o
