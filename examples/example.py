import sys
sys.path.append('../pyclk')
from pyclk import Module, Sig, In, Out, Reg

class Passthrough(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name, 'passthrough'):
            self.sig0 = Sig('sig0')
            self.in0 = In('in0')
            self.out0 = Out('out0')
    def logic(self):
        self.out0.v = self.in0.v

class Toplevel(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name, 'toplevel'):
            # declare signals, registers, I/Os:
            self.in0 = In('in0')
            self.out0 = Out('out0')
            self.sig0 = Sig('sig0')
            self.reg0 = Reg('reg0')
            self.reg1 = Reg('reg1')
            # instanciate sub-modules and make connections:
            self.i_passthrough1 = Passthrough('i_passthrough1')
            self.i_passthrough1.in0(self.in0)
            self.i_passthrough1.out0(self.sig0)
            self.i_passthrough2 = Passthrough('i_passthrough2')
            self.i_passthrough2.in0(self.reg1)
            self.i_passthrough2.out0(self.out0)
    def logic(self):
        # logic goes here:
        self.reg0.d = self.sig0.v + 3
        self.reg1.d = self.reg0.q + 1

i_toplevel = Toplevel('i_toplevel')

for _ in range(3):
    i_toplevel.run(1)
    print(i_toplevel.out0)
