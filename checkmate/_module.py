import os
import imp
import sys
import importlib


def get_module(current_name, new_name, current_path, new_path):
    basename = current_name.split('.')[-1]
    _fullname = current_path + '.' + basename
    _new_fullname = new_path + '.' + new_name
    _file = sys.modules[current_name].__file__
    module_name = current_name.replace(_fullname, _new_fullname)
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        module = imp.new_module(module_name)
        module.__name__ = module_name
        module.__file__ = _file.replace(_fullname.replace('.', os.sep), _new_fullname.replace('.', os.sep))
        sys.modules[module_name] = module
        setattr(importlib.import_module(current_name.replace(_fullname, new_path), current_name.replace(_fullname, '')), new_name, module)
    return module

