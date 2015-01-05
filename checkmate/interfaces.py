import zope.interface


class IExchange(zope.interface.Interface):
    """"""


class IComponent(zope.interface.Interface):
    """"""


class IRun(zope.interface.Interface):
    """"""


class IState(zope.interface.Interface):
    """"""
    def append(self, *args, **kwargs):
        """"""

    def toggle(self, *args, **kwargs):
        """"""

    def flush(self, *args, **kwargs):
        """"""

    def up(self, *args, **kwargs):
        """"""

    def down(self, *args, **kwargs):
        """"""

    def pop(self, *args, **kwargs):
        """"""


class IStorage(zope.interface.Interface):
    """"""
    def factory(self, args=[], kwargs={}):
        """"""


class ITree(zope.interface.Interface):
    """"""

