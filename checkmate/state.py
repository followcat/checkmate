import zope.interface.interface

import checkmate.partition


def toggle(self, *args, **kwargs):
    """Change the value of the state

    Should only be used on State with 2 values
    """
    if self.value is not None:
        self.value = self._valid_values[(len(self._valid_values)-1) - (self._valid_values.index(self.value))]

def append(self, *args, **kwargs):
    """
        >>> setattr(State, 'append', append)
        >>> s = State()
        >>> s.append('Q')
        >>> s.value
        ['Q']
        >>> delattr(State, 'append')
    """
    if self.value is None:
        self.value = []
    elif (len(self.value) == 1 and self.value[0] == None):
        self.value = []
    elif type(self.value) != list:
        self.value = list([self.value])

    try:
        if len(kwargs) == 0:
            if len(args) == 0:
                return
            value = args[0]
            if ((type(value) == str and value == 'None') or
                value is None):
                return
            if value not in self.value:
                self.value.append(value)
        else:
            for key, value in list(kwargs.items()):
                if {key: value} not in self.value:
                    self.value.append({key: value})
                    setattr(self, key, value)
    except:
        pass

def pop(self, *args, **kwargs):
    """
        >>> setattr(State, 'pop', pop)
        >>> s = State('R')
        >>> s.value
        ['R']
        >>> s.pop()
        'R'
        >>> s.value
        []
        >>> delattr(State, 'pop')
    """
    try:
        value = args[0]
    except:
        value = None
    if type(self.value) != list:
        self.value = list([self.value])
    try:
        if len(kwargs) == 0:
            if value is None:
                return self.value.pop(0)
            else:
                return self.value.pop(self.value.index(value))
        else:
            for value in list(kwargs.items()):
                return self.value.pop(self.value.index({value[0]: value[1]}))
    except:
        return None

def flush(self, *args, **kwargs):
    """
        >>> setattr(State, 'append', append)
        >>> setattr(State, 'flush', flush)
        >>> s = State()
        >>> s.append('P')
        >>> s.append('R')
        >>> s.value
        ['P', 'R']
        >>> s.flush('P')
        >>> s.value
        ['R']
        >>> delattr(State, 'append')
        >>> delattr(State, 'flush')
    """
    try:
        value = args[0]
    except:
        self.value = []
        return
    if type(self.value) != list:
        self.value = list([self.value])
    count = self.value.count(value)
    for i in range(0, count):
        self.value.remove(value)

def up(self, *args, **kwargs):
    """
        >>> setattr(State, 'append', append)
        >>> setattr(State, 'up', up)
        >>> s.append('R')
        >>> s.append('P')
        >>> s.append('S')
        >>> s.value
        ['R', 'P', 'S']
        >>> s.up('S')
        >>> s.value
        ['R', 'S', 'P']
        >>> delattr(State, 'append')
        >>> delattr(State, 'up')
    """
    try:
        value = args[0]
    except:
        value = None
    if type(self.value) != list:
        self.value = list([self.value])
    try:
        index = self.value.index(value)
        return self.value.insert(index-1, self.value.pop(index))
    except:
        pass

def down(self, *args, **kwargs):
    """
        >>> setattr(State, 'append', append)
        >>> setattr(State, 'down', down)
        >>> s = State()
        >>> s.append('R')
        >>> s.append('P')
        >>> s.append('S')
        >>> s.value
        ['R', 'P', 'S']
        >>> s.down('P')
        >>> s.value
        ['R', 'S', 'P']
        >>> delattr(State, 'append')
        >>> delattr(State, 'down')
    """
    try:
        value = args[0]
    except:
        value = None
    if type(self.value) != list:
        self.value = list([self.value])
    try:
        index = self.value.index(value)
        return self.value.insert(index+1, self.value.pop(index))
    except:
        pass


class State(checkmate.partition.Partition):
    """"""
    _valid_values = [False, True]
    _queue = False

    def __init__(self, value=None, *args, **kwargs):
        """State object supports value=None for state matching

            >>> setattr(State, 'append', append)
            >>> s = State()
            >>> s._queue
            True
            >>> delattr(State, 'append')
        """
        super(State, self).__init__(value, *args, **kwargs)

    def __eq__(self, other):
        """
            >>> setattr(State, 'append', append)
            >>> setattr(State, 'pop', pop)
            >>> s1 = State(); s2 = State('R')
            >>> s1 == s2
            True
            >>> s1.append('Q')
            >>> s1 == s2
            False
            >>> q = s1.pop(); s1.append('R')
            >>> s1 == s2
            True
            >>> s1.append('Q')
            >>> s1 == s2
            False
            >>> r = s1.pop(); q = s1.pop(); s1.append(R=None)
            >>> s1 == s2
            False
            >>> r = s2.pop(); s1.append(R=1)
            >>> s1 == s2
            False
            >>> delattr(State, 'append')
            >>> delattr(State, 'pop')
        """
        return super(State, self).__eq__(other)
