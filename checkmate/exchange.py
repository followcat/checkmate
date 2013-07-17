import zope.interface.interface


def new_exchange(name, parents, param):
    return type(name, parents, param)

def new_exchange_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class Exchange(object):
    """"""
    _default_description = (None, None, None)
    _description = {}
    def __init__(self, action, *args, **kwargs):
        self.action = action
        self.args = args
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        return self.action == other.action

    def description(self):
        for key in self._description.keys():
            if self == self._description[key][0].factory():
                return self._description[key][-1]
        return (None,None,None)

