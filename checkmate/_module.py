# This code is part of the checkmate project.
# Copyright (C) 2014-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import imp
import sys
import importlib


def get_module(package_name, module_name, alternative_package=None):
    """Load existing module or create a new one

    The provided package_name is expected to be a sub-package
    under the project main package (eg. 'main.sub').

    This function can be used to create a module in an alternative
    package beside the provided one:
        >>> import checkmate._module
        >>> import sample_app.application
        >>> mod = checkmate._module.get_module(
        ...         'sample_app.application', 'xxx', 'component')
        >>> mod # doctest: +ELLIPSIS
        <module 'sample_app.component.xxx' from ...

    It can also be used to create a new module beside an existing one
    in the provided package:
        >>> mod2 = checkmate._module.get_module(
        ...             'sample_app.component.xxx', 'yyy')
        >>> mod2 # doctest: +ELLIPSIS
        <module 'sample_app.component.yyy' from ...

        >>> mod3 = checkmate._module.get_module(
        ...             'checkmate.application', 'data')
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

    try: 
        module = importlib.import_module(_name)
    except ImportError:
        module = imp.new_module(_name)
        module.__name__ = _name
        module.__file__ = _file.replace(_fullname.replace('.', os.sep),
                            _new_fullname.replace('.', os.sep))
        sys.modules[_name] = module
        setattr(
            importlib.import_module(
                package_name.replace(_fullname, alternative_package),
                package_name.replace(_fullname, '')), 
            module_name,
            module)
    return module

