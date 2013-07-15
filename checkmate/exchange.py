import zope.interface.interface


def new_exchange(name, parents, param):
    return type(name, parents, param)

def new_exchange_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class Exchange(object):
    """"""
    def __init__(self, action, *args, **kwargs):
        self.action = action
        self.args = args
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        return self.action == other.action

    def description(self):
        if self.action in self._description.keys():
            return self._description[self.action]
        return (None,None,None)

