import os
import imp
import sys
import importlib


def get_module(package_name, module_name, alternative_package=None):
    """
        >>> import checkmate._module
        >>> import sample_app.application
        >>> mod = checkmate._module.get_module('sample_app.application', 'xxx', '.component')
        >>> mod # doctest: +ELLIPSIS
        <module 'sample_app.component.xxx' from ...
        >>> mod2 = checkmate._module.get_module('sample_app.component.xxx', 'yyy')
        >>> mod2 # doctest: +ELLIPSIS
        <module 'sample_app.component.yyy' from ...
    """
    basename = package_name.split('.')[-1]
    if alternative_package == None:
        alternative_package = '.' + package_name.split('.')[-2]
        target_package = alternative_package
    else:
        target_package = ''
    _fullname = target_package + '.' + basename
    _new_fullname = alternative_package + '.' + module_name
    _file = sys.modules[package_name].__file__
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

