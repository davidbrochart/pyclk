This is a simple implementation of Hardware Description Language (HDL).

```python
import sys
sys.path.append('../pyclk')
from pyclk import Module, Sig, In, Out, Reg

class Passthrough(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name, 'passthrough'):
            Sig('sig0')
            In('in0')
            Out('out0')
    def logic(self):
        self.out0.d = self.in0.d

class Toplevel(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name, 'toplevel'):
            # declare signals, registers, I/Os:
            In('in0')
            Out('out0')
            Sig('sig0')
            Reg('reg0')
            Reg('reg1')
            # instanciate sub-modules and make connections:
            _ = Passthrough('i_passthrough1')
            _.in0     ('in0')
            _.out0    ('sig0')
            _ = Passthrough('i_passthrough2')
            _.in0     ('reg1')
            _.out0    ('out0')
    def logic(self):
        # logic goes here:
        self.reg0.d = self.sig0.d + 3
        self.reg1.d = self.reg0.q + 1

i_toplevel = Toplevel('i_toplevel')

for _ in range(3):
    i_toplevel.run(1)
    print(i_toplevel.out0)
```

```
Output i_toplevel.out0: d == 0
Output i_toplevel.out0: d == 1
Output i_toplevel.out0: d == 4
```
