class Partition(object):
    """"""
    _queue = False

    def __init__(self, value=None, *args, **kwargs):
        """
            >>> ds = Partition('AT1')
            >>> ds.value
            'AT1'
        """
        if hasattr(self, 'append'):
            self._queue = True
        if self._queue == True:
            # intended to be a 'None' string
            if (type(value) == str and value == 'None'):
                value = []
            if type(value) == list:
                self.value = list(value)
            else:
                self.value = [value]
        else:
            self.value = value
            if value is None:
                try:
                    self.value = self._valid_values[0]
                except:
                    pass
            
        self.args = args
        for key in list(kwargs.keys()):
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        """
            >>> Partition('AT1') == Partition('AT2')
            False
            >>> Partition('AT1') == Partition('AT1')
            True
        """
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
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

