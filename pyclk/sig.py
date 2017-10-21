from pyclk import Val

class Sig:
    def __init__(self, name=''):
        self.name = name
        self._driver = None
        self._mod = None
        self._vkeep = 0
        self._val = Val()
    def get_path(self):
        ret = ''
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        ret += self.name
        return ret
    @property
    def d(self):
        return self._val.v
    @d.setter
    def d(self, val):
        if issubclass(type(val), Sig):
            self._val.v = val._val.v
        else:
            self._val.v = val
    def __eq__(self, other):
        return self._val.v == other
    def __neq__(self, other):
        return self._val.v != other
    def __repr__(self):
        ret = ''
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        ret += f'{self.name}: d == {self.d}'
        return ret
