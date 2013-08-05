import functools

import zope.interface

import checkmate._utils
import checkmate._storage


def _to_interface(_classname):
    return 'I'+_classname


class Declarator(object):
    def __init__(self, data_module, state_module=None, exchange_module=None,
                       transition_module=None):
        self.module = {}
        self.module['data_structure'] = data_module
        self.module['states'] = state_module
        self.module['exchanges'] = exchange_module

        self.basic_modules = {}
        self.basic_modules['data_structure'] = [data_module]
        self.basic_modules['states'] = [data_module]
        self.basic_modules['exchanges'] = [data_module, state_module]

    def new_partition(self, partition_type, signature, codes, full_description):
        standard_methods = {}
        if checkmate._utils.is_method(signature):
            classname = checkmate._utils._leading_name(signature)
            for class_attr in checkmate._utils.method_arguments(signature)[0]:
                for _module in self.basic_modules[partition_type]:
                    try:
                        interface = getattr(_module, _to_interface(class_kwattr))
                        standard_methods.update({class_attr: checkmate._storage.store_data_structure(interface, class_attr)})
                        break
                    except AttributeError:
                        continue
            for key, class_kwattr in checkmate._utils.method_arguments(signature)[1].items():
                for _module in self.basic_modules[partition_type]:
                    try:
                        interface = getattr(_module, _to_interface(class_kwattr))
                        standard_methods.update({key: checkmate._storage.store_data_structure(interface, class_kwattr)})
                        break
                    except AttributeError:
                        continue
        else:
            classname = signature

        _module = self.module[partition_type]
        standard_methods.update({'_valid_values': [checkmate._utils.valid_value_argument(_v) for _v in codes if checkmate._utils.valid_value_argument(_v) is not None]})
        setattr(_module, classname, _module.declare(classname, standard_methods))
        setattr(_module, _to_interface(classname), _module.declare_interface(_to_interface(classname), {}))
        zope.interface.classImplements(getattr(_module, classname), [getattr(_module, _to_interface(classname))])

        interface = getattr(_module, _to_interface(classname))
        cls = checkmate._utils.get_class_implementing(interface)
        for code in codes:
            if ((partition_type == 'exchanges') and (checkmate._utils.is_method(code))):
                setattr(_module, checkmate._utils.internal_code(code), functools.partial(cls, checkmate._utils.internal_code(code)))

        partition_storage = checkmate._storage.PartitionStorage(partition_type, interface, codes, full_description)
        setattr(cls, 'partition_storage', partition_storage)

        # Return storage for compatibility only
        return (interface, partition_storage)

