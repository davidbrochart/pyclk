class List:
    def __init__(self):
        self._list = {}
        self.name = ''
        self._mod = None
    def __getitem__(self, key):
        if self._mod is not None:
            name = self.name + str(key)
            return self._mod.__dict__[name]
        else:
            return self._list[key]
    def __setitem__(self, key, val):
        if self._mod is not None:
            name = self.name + str(key)
            self._mod.__setattr__(name, val)
        else:
            self._list[key] = val
