import sys
sys.path.append('../pyclk')
from pyclk import Module, Sig, In, Out, Reg

class counter(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name):
            In  ('i_rst')
            Out ('o_cnt')
            Reg ('r_cnt')
    def logic(self):
        # logic goes here:
        if self.i_rst == 1:
            self.r_cnt = 0
        else:
            self.r_cnt = self.r_cnt.q + 1
        self.o_cnt = self.r_cnt.q

class toplevel(Module):
    def __init__(self, inst_name):
        with self.setup(inst_name):
            # declare signals, registers, I/Os:
            In  ('i_rst1')
            In  ('i_rst2')
            Out ('o_cnt1')
            Out ('o_cnt2')
            # instanciate sub-modules and make connections:
            _ = counter ('u_counter1')
            _.i_rst     ('i_rst1')
            _.o_cnt     ('o_cnt1')
            _ = counter ('u_counter2')
            _.i_rst     ('i_rst2')
            _.o_cnt     ('o_cnt2')

u_toplevel = toplevel('u_toplevel')

u_toplevel.i_rst1 = 1
u_toplevel.i_rst2 = 1

t = 0

def print_run():
    global t
    print(f'**************************************** time == {t}')
    u_toplevel.run()
    print(u_toplevel.o_cnt1)
    print(u_toplevel.o_cnt2)
    t += 1

for _ in range(3):
    print_run()

u_toplevel.i_rst1 = 0

print_run()

u_toplevel.i_rst2 = 0

for _ in range(5):
    print_run()
