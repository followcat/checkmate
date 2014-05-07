import os
import imp
import sys
import inspect
import importlib

import checkmate._utils


def exec_class_definition(partition_type, exec_module, classname, standard_methods, interface_class, codes):
    module_class_map = {
        'exchanges':'checkmate.exchange.Exchange',
        'data_structure':'checkmate.data_structure.DataStructure',
        'states':'checkmate.state.State'
    }
    module_class = module_class_map[partition_type]
    import_module = 'import ' + '.'.join(module_class.split('.')[:-1])

    run_code = """
            \nimport zope.interface.interface
            \n%s\n
            \nclass %s(zope.interface.Interface):
            \n    \"\"\"\"\"\"
            """ % (import_module, interface_class)

    run_code += """
            \n@zope.interface.implementer(%s)
            \nclass %s(%s):
            \n    def __init__(self, *args, **kwargs):
            \n        super().__init__(*args, **kwargs)
            """ % (interface_class, classname, module_class)

    if partition_type == 'exchanges':
        for code in codes:
            if checkmate._utils.is_method(code):
                internal_code = checkmate._utils.internal_code(code)
                run_code += """
                \ndef %s(*args, **kwargs):
                \n    return %s('%s', *args, **kwargs)
                """ % (internal_code, classname, internal_code)

    exec(run_code, exec_module.__dict__)
    define_class = getattr(exec_module, classname)
    define_interface = getattr(exec_module, 'I' + classname)
    for _k, _v in standard_methods.items():
        setattr(define_class, _k, _v)

    return define_class, define_interface


def get_module(package_name, module_name, alternative_package=None):
    """Load existing module or create a new one

    The provided package_name is expected to be a sub-package
    under the project main package (eg. 'main.sub').

    This function can be used to create a module in an alternative package beside the provided one:
        >>> import checkmate._module
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

    if alternative_package == None:
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
