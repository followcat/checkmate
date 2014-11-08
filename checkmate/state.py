import zope.interface.interface

import checkmate.partition


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


@zope.interface.implementer(IState)
class State(checkmate.partition.Partition):
    """"""

    def __init__(self, value=None, *args, **kwargs):
        """State object supports value=None for state matching
        """
        super(State, self).__init__(value, *args, **kwargs)

    def __eq__(self, other):
        """
            import checkmate.state
            >>> s1 = checkmate.state.State(); s2 = checkmate.state.State()
            >>> s2.append('R')
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
        """
        return super(State, self).__eq__(other)


    @checkmate.fix_issue('checkmate/issues/first_append_result.rst')
    def append(self, *args, **kwargs):
        """
            >>> s = State()
            >>> s.append('Q')
            >>> s.value
            ['Q']
        """
        if self.value == 'None' or self.value is None:
            self.value = []
        if not isinstance(self.value, list):
            self.value = list([self.value])

        try:
            if len(kwargs) == 0:
                if len(args) == 0:
                    return
                value = args[0]
                if value == 'None' or value is None:
                    return
                if value not in self.value:
                    self.value.append(value)
                    setattr(self, key, value)
            else:
                for key, value in list(kwargs.items()):
                    if {key: value} not in self.value:
                        self.value.append({key: value})
        except:
            pass

    def toggle(self, *args, **kwargs):
        """Change the value of the state

        Should only be used on State with 2 values
        """
        if self.value is None:
            try:
                self.value = self._valid_values[0]
            except:
                pass
        if self.value is not None:
            self.value = self._valid_values[(len(self._valid_values) - 1) - (self._valid_values.index(self.value))]

    def flush(self, *args, **kwargs):
        """
            >>> s = State()
            >>> s.append('P')
            >>> s.append('R')
            >>> s.value
            ['P', 'R']
            >>> s.flush('P')
            >>> s.value
            ['R']
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
            >>> s = State()
            >>> s.append('R')
            >>> s.append('P')
            >>> s.append('S')
            >>> s.value
            ['R', 'P', 'S']
            >>> s.up('S')
            >>> s.value
            ['R', 'S', 'P']
        """
        try:
            value = args[0]
        except:
            value = None
        if type(self.value) != list:
            self.value = list([self.value])
        try:
            index = self.value.index(value)
            return self.value.insert(index - 1, self.value.pop(index))
        except:
            pass

    def down(self, *args, **kwargs):
        """
            >>> s = State()
            >>> s.append('R')
            >>> s.append('P')
            >>> s.append('S')
            >>> s.value
            ['R', 'P', 'S']
            >>> s.down('P')
            >>> s.value
            ['R', 'S', 'P']
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

    def pop(self, *args, **kwargs):
        """
            >>> s = State()
            >>> s.append('R')
            >>> s.value
            ['R']
            >>> s.pop()
            'R'
            >>> s.value
            []
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
