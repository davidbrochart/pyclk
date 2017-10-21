from pyclk import Sig

class Out(Sig):
    def __init__(self, name=''):
        super().__init__(name=name)
    def __call__(self, sig):
        if sig._driver is not None:
            raise AttributeError(f'Out {sig.name} already connected to {sig._driver.name}')
        sig._driver = self
        sig._val = self._val
