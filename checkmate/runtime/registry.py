import zope.component.globalregistry


class RuntimeGlobalRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """
    """
    def __init__(self):
        super(RuntimeGlobalRegistry, self).__init__()

