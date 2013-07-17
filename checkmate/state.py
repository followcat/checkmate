import zope.interface.interface


def toggle(self):
    """Change the value of the state

    Should only be used on State with 2 values
    """
    if self.value is not None:
        self.value = self._valid_values[(len(self._valid_values)-1) - (self._valid_values.index(self.value))]

def append(self, *args):
    try:
        value = args[0]
    except:
        value = None
    if self.value is None:
        self.value = []
    elif (len(self.value) == 1 and self.value[0] == None):
        self.value = []
    elif type(self.value) != list:
        self.value = list([self.value])
    if value not in self.value:
        self.value.append(value)

def pop(self, *args):
    try:
        value = args[0]
    except:
        value = None
    if type(self.value) != list:
        self.value = list([self.value])
    try:
        if value is None:
            return self.value.pop(-1)
        else:
            return self.value.pop(self.value.index(value))
    except:
        return None

class State(object):
    """"""
    _valid_values = [False, True]
    _queue = False

    def __init__(self, value=None, *args, **kwargs):
        """State object supports value=None for state matching"""
        if hasattr(self, 'append'):
            self._queue = True
        if self._queue == True:
            # intended to be a 'None' string
            if ((type(value) == str or type(value) == unicode) and value == 'None'):
                value = []
            if type(value) == list:
                self.value = list(value)
            else:
                self.value = [value]
        else:
            self.value = value
        self.args = args
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        if self._queue == True:
            if len(self.value) == 0:
                return (len(other.value) == 0 or other.value[0] == None)
            elif len(other.value) == 0:
                return (len(self.value) == 0 or self.value[0] == None)
            elif self.value[0] == None or other.value[0] == None:
                return True
            else:
                return (self.value == other.value)
        if self.value == None or other.value == None:
            return True
        else:
            return (self.value == other.value)

    def description(self):
        for key in self._description.keys():
            if self == self._description[key][0].factory():
                return self._description[key][-1]
        return (None,None,None)

def declare(name, param):
    return type(name, (State,), param)

def declare_interface(name, param):
    return zope.interface.interface.InterfaceClass(name, (zope.interface.Interface,), param)

