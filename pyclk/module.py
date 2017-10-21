import types
from pyclk import Sig, Reg, In, Out, List

class Module:
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
        elif type(val) is List:
            self.__dict__[name] = val
            self.__dict__[name].name = name
            self.__dict__[name]._mod = self
        elif issubclass(type(val), Module):
            self.__dict__[name] = val
            self.__dict__[name].name = name
            self.__dict__[name]._parent = self
            self._modules.append(val)
        elif issubclass(type(val), Sig):
            self.__dict__[name] = val
            self.__dict__[name].name = name
            self.__dict__[name]._mod = self
            self._signals.append(val)
        else:
            self.__dict__[name] = val
    def _init(self):
        self.time = 0
        self.module_name = self.__class__.__name__
        self.name = ''
        self._parent = None
        self._first_run = True
        self._signals = []
        self._modules = []
        self._generators = []
        self._can_run = -1 # 0: cannot run, -1: can run forever, >0: can run for nb of clk
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self._init()
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
    def task(self):
        pass
    def wait(self, clkNb=1):
        self._can_run = clkNb
        while self._can_run != 0:
            yield
    def run(self, clkNb=1, trace=None):
        if self._first_run:
            self._bind()
            for mod in self.iter_modules():
                g = mod.task()
                if type(g) is types.GeneratorType:
                    mod._generators.append(g)
        for _ in range(clkNb):
            # advance clock one cycle:
            for mod in self.iter_modules():
                for sig in mod._signals:
                    if type(sig) is Reg:
                        sig._q.v = sig._val.v
            # execute tasks:
            for mod in self.iter_modules():
                if len(mod._generators) > 0:
                    done = False
                    while not done:
                        try:
                            g = next(mod._generators[-1])
                            if type(g) is types.GeneratorType:
                                mod._generators.append(g)
                            else:
                                done = True
                        except StopIteration:
                            mod._generators.pop()
                            if len(mod._generators) > 0:
                                g = mod._generators[-1]
                            else:
                                done = True
                if mod._can_run >= 0:
                    mod._can_run -= 1
            # execute logic:
            done = False
            while not done:
                done = True
                for mod in self.iter_modules():
                    for sig in mod._signals:
                        if (type(sig) is In) or (type(sig) is Out):
                            if self._first_run:
                                done = False
                            elif sig._val.v != sig._vkeep:
                                done = False
                            if not done:
                                sig._vkeep = sig._val.v
                    mod.logic()
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
            for mod in self.iter_modules():
                mod.time += 1
    def _bind(self):
        for mod in self.iter_modules():
            for sig in mod._signals:
                prev_sig = sig
                while prev_sig._driver is not None:
                    prev_sig = prev_sig._driver
                if prev_sig != sig:
                    if type(prev_sig) is Reg:  # when connected to a Reg
                        sig._val = prev_sig._q # driver is q
                    else:
                        sig._val = prev_sig._val
    def iter_modules(self):
            new_modules = []
            pending_modules = [self]
            while len(pending_modules) > 0:
                for mod in pending_modules:
                    yield mod
                    new_modules += mod._modules
                pending_modules = new_modules
                new_modules = []
