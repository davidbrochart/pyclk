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
    def __repr__(self):
        if type(self) is Reg:
            ret = f'Register '
        elif type(self) is Sig:
            ret = f'Signal '
        elif type(self) is In:
            ret = f'Input '
        elif type(self) is Out:
            ret = f'Output '
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        if type(self) is Reg:
            ret += f'{self.name}: d == {self.d}, q == {self.q}'
        else:
            ret += f'{self.name}: v == {self.v}'
        return ret

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

class In(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
    def __call__(self, sig):
        if self._driver is not None:
            path1 = ''
            if self._mod is not None:
                path1 += self._mod.get_path() + '.'
            path2 = ''
            if self._driver._mod is not None:
                path2 += self._driver._mod.get_path() + '.'
            raise AttributeError(f'Input {path1}{self.name} already connected to {path2}{self._driver.name}')
        self._driver = sig

class Out(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
    def __call__(self, sig):
        if sig._driver is not None:
            raise AttributeError(f'Out {sig.name} already connected to {sig._driver.name}')
        sig._driver = self
        sig._val = self._val

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
        self._first_run = True
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
    def logic(self):
        pass
    def run(self, clkNb=1):
        for _ in range(clkNb):
            # registers:
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
            # logic:
            done = False
            pending_modules = []
            while not done:
                done = True
                pending_modules.append(self)
                while len(pending_modules) > 0:
                    for mod in pending_modules:
                        for sig in mod._signals:
                            if (type(sig) is In) or (type(sig) is Out):
                                if self._first_run:
                                    done = False
                                elif sig._val.v != sig._vkeep:
                                    done = False
                                if not done:
                                    sig._vkeep = sig._val.v
                        mod.logic()
                        new_modules += mod._modules
                    pending_modules = new_modules
                    new_modules = []
                self._first_run = False
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
                        if type(prev_sig) is Reg:  # when connected to a Reg
                            sig._val = prev_sig._q # driver is q
                        else:
                            sig._val = prev_sig._val
                new_modules += mod._modules
            pending_modules = new_modules
            new_modules = []
