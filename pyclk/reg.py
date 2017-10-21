from pyclk import Sig, Val

class Reg(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
        self._q = Val()
    @property
    def d(self):
        return self._val.v
    @d.setter
    def d(self, val):
        if issubclass(type(val), Sig):
            self._val.v = val._val.v
        else:
            self._val.v = val
    @property
    def q(self):
        return self._q.v
    def __eq__(self, other):
        return self._q.v == other
    def __neq__(self, other):
        return self._q.v != other
    def __repr__(self):
        ret = ''
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        ret += f'{self.name}: d == {self.d}, q == {self.q}'
        return ret
