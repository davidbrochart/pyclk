_global_modules = []

class Val:
    def __init__(self, val=0):
        self.v = val

class Sig:
    def __init__(self, name=''):
        self.name = name
        self._driver = None
        self._mod = None
        self._vkeep = 0
        self._val = Val()
        if len(_global_modules) > 0:
            _global_modules[-1]._signals.append(self)
    @property
    def v(self):
        return self._val.v
    @v.setter
    def v(self, val):
        if issubclass(type(val), Sig):
            self._val.v = val._val.v
        else:
            self._val.v = val
    def _repr(self, _type):
        ret = f'{_type} '
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        ret += f'{self.name} == {self.v}'
        return ret
    def __repr__(self):
        return self._repr('Signal')

class Reg(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
        self._q = Val()
    @property
    def v(self):
        raise AttributeError(f"""Attribute "v" doesn't exist for Reg {self.name}, use "d" or "q" instead""")
    @v.setter
    def v(self, val):
        raise AttributeError(f"""Attribute "v" doesn't exist for Reg {self.name}, use "d" instead""")
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
    def __repr__(self):
        return self._repr('Register')

class In(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
    def __call__(self, sig):
        if self._driver is not None:
            raise AttributeError(f'In {self.name} already connected to {self._driver.name}')
        self._driver = sig
    def __repr__(self):
        return self._repr('Input')

class Out(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
    def __call__(self, sig):
        if sig._driver is not None:
            raise AttributeError(f'Out {sig.name} already connected to {sig._driver.name}')
        sig._driver = self
        sig._val = self._val
    def __repr__(self):
        return self._repr('Output')

class Module:
    def __enter__(self):
        pass
    def __exit__(self, *args):
        _global_modules.pop()
        self._bind()
    def setup(self, inst_name='', name=''):
        self.inst_name = inst_name
        self.name = name
        self._parent = None
        self._first_compute = True
        self._signals = []
        self._modules = []
        if len(_global_modules) > 0:
            _global_modules[-1]._modules.append(self)
            self._parent = _global_modules[-1]
        _global_modules.append(self)
        return self
    def get_path(self):
        path = [self.inst_name]
        parent = self._parent
        while parent is not None:
            path.append(parent.inst_name)
            parent = parent._parent
        path = '.'.join(path[::-1])
        return path
    def compute(self):
        pass
    def run(self, clkNb=1):
        for _ in range(clkNb):
            # update:
            new_modules = []
            pending_modules = [self]
            while len(pending_modules) > 0:
                for mod in pending_modules:
                    for sig in mod._signals:
                        if type(sig) is Reg:
                            sig._q.v = sig._val.v
                    new_modules += mod._modules
                pending_modules = new_modules
                new_modules = []
            # compute:
            done = False
            pending_modules = []
            while not done:
                done = True
                pending_modules.append(self)
                while len(pending_modules) > 0:
                    for mod in pending_modules:
                        for sig in mod._signals:
                            if (type(sig) is In) or (type(sig) is Out):
                                if self._first_compute:
                                    done = False
                                elif sig._val.v != sig._vkeep:
                                    done = False
                                if not done:
                                    sig._vkeep = sig._val.v
                        mod.compute()
                        new_modules += mod._modules
                    pending_modules = new_modules
                    new_modules = []
                self._first_compute = False
    def _bind(self):
        pending_modules = [self]
        new_modules = []
        while len(pending_modules) > 0:
            for mod in pending_modules:
                for sig in mod._signals:
                    if mod == self:
                        sig._mod = self
                    prev_sig = sig
                    while prev_sig._driver is not None:
                        prev_sig = prev_sig._driver
                    if prev_sig != sig:
                        if type(prev_sig) is Reg: # when connected to a Reg
                            sig._val = prev_sig._q # driver is q
                        else:
                            sig._val = prev_sig._val
                new_modules += mod._modules
            pending_modules = new_modules
            new_modules = []
