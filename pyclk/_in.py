from pyclk import Sig

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
