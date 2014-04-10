import zope.component.globalregistry


class RuntimeGlobalRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """
    """
    def __init__(self):
        super(RuntimeGlobalRegistry, self).__init__()
        global_registry = self

global_registries_dict = {}

def get_registry(reg_key):
    try:
        return global_registries_dict[reg_key]
    except AttributeError as e:
        raise e("No registry found for %s" %reg_key)
