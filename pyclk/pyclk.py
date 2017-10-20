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
            self._mod = _global_modules[-1]
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
        if type(self) is Reg:
            return self._q.v == other
        else:
            return self._val.v == other
    def __neq__(self, other):
        if type(self) is Reg:
            return self._q.v != other
        else:
            return self._val.v != other
    def __repr__(self):
        if type(self) is Reg:
            ret = 'register '
        elif type(self) is Sig:
            ret = 'signal '
        elif type(self) is In:
            ret = 'input '
        elif type(self) is Out:
            ret = 'output '
        if self._mod is not None:
            ret += self._mod.get_path() + '.'
        if type(self) is Reg:
            ret += f'{self.name}: d == {self.d}, q == {self.q}'
        else:
            ret += f'{self.name}: d == {self.d}'
        return ret

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
        for k, v in self.__dict__.items():
            if id(v) in [id(sig) for sig in self._signals] or id(v) in [id(mod) for mod in self._modules]:
                v.name = k
    def __setattr__(self, name, val):
        if name in self.__dict__:
            if issubclass(type(self.__dict__[name]), Sig):
                if issubclass(type(val), Sig):
                    sig = val
                    if type(sig) is Reg:
                        self.__dict__[name]._val.v = sig._q.v
                    else:
                        self.__dict__[name]._val.v = sig._val.v
                else:
                    self.__dict__[name]._val.v = val
            else:
                self.__dict__[name] = val
        else:
            self.__dict__[name] = val
    def setup(self):
        self.time = 0
        self.module_name = self.__class__.__name__
        self.name = 'u_' + self.module_name
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
        path = [self.name]
        parent = self._parent
        while parent is not None:
            path.append(parent.name)
            parent = parent._parent
        path = '.'.join(path[::-1])
        return path
    def logic(self):
        pass
    def run(self, clkNb=1, trace=None):
        if self._first_run:
            self._bind()
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
                if self._first_run:
                    self._first_run = False
            if trace is not None:
                for i, sig in enumerate(trace._signals):
                    if trace._traces[i]['enable']:
                        trace._traces[i]['time'].append(self.time)
                        if type(sig) is Reg:
                            trace._traces[i]['val'].append(sig._q.v)
                        else:
                            trace._traces[i]['val'].append(sig._val.v)
            self.time += 1
    def _bind(self):
        pending_modules = [self]
        new_modules = []
        while len(pending_modules) > 0:
            for mod in pending_modules:
                for sig in mod._signals:
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

class Trace:
    def __init__(self):
        self._traces = []
        self._signals = []
    def add(self, sig):
        if id(sig) in [id(s) for s in self._signals]:
            i = self._signals.index(sig)
            self._traces[i]['enable'] = True
        else:
            self._signals.append(sig)
            self._traces.append({'time': [], 'val': [], 'enable': True})
    def remove(self, sig):
        i = self._signals.index(sig)
        self._traces[i]['enable'] = False
    def plot(self, figsize=None, full_path=False):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(len(self._traces), sharex=True)
        if figsize is None:
            figsize = (15, 2 * len(self._traces))
        fig.set_size_inches(figsize)
        fig.subplots_adjust(hspace=0)
        for i, sig in enumerate(self._signals):
            path = sig.get_path()
            x = list(self._traces[i]['time'])
            y = list(self._traces[i]['val'])
            j = 0
            while j < len(x):
                if j + 1 == len(x):
                    x.insert(j + 1, x[j] + 1)
                    y.insert(j + 1, y[j])
                else:
                    if x[j + 1] - x[j] > 1:
                        x.insert(j + 1, x[j] + 1)
                        y.insert(j + 1, y[j])
                        j += 1
                        x.insert(j + 1, None)
                        y.insert(j + 1, None)
                    else:
                        x.insert(j + 1, x[j + 1])
                        y.insert(j + 1, y[j])
                j += 2
            ax[i].plot(x, y)
            if full_path:
                ax[i].set_ylabel(path)
            else:
                ax[i].set_ylabel(path[path.rfind('.') + 1:])
        plt.show()
