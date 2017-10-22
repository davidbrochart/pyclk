PyClk is a simple implementation of a Hardware Description Language (HDL) in Python. In industry standard HDLs such as SystemC, Verilog and VHDL (and also [MyHDL](http://www.myhdl.org)), the clock is modeled just as any other signal in the design. On the contrary, the clock signal in PyClk is special in that it is implicit and it does not actually exist: calling `run()` makes the clock advance one cycle. This simplifies the implementation of PyClk and probably improves its performances, but it also makes your design clearer: a register is declared explicitly, and not infered from the way it is used. On the other hand, this implies that your whole design works with a single clock. Although multiple clocks might be supported in the future, you can already do a lot with just one clock!

```python
import sys
sys.path.append('..')
from pyclk import Module, List, In, Out, Reg, Trace
```


```python
class counter(Module):
    def __init__(self):
        self.i_rst = In()
        self.o_cnt = Out()
        self.r_cnt = Reg()
    def logic(self):
        # logic goes here
        if self.i_rst == 1:
            self.r_cnt = 0
        else:
            self.r_cnt = self.r_cnt.q + 1
        self.o_cnt = self.r_cnt.q

class top(Module):
    def __init__(self):
        # declare signals, registers, I/Os
        # instanciate sub-modules and make connections
        self.i_rst = List()
        self.o_cnt = List()
        self.u_counter = List()
        for i in range(2):
            self.i_rst[i] = In()
            self.o_cnt[i] = Out()
            self.u_counter[i] = _ = counter()
            _.i_rst(self.i_rst[i])
            _.o_cnt(self.o_cnt[i])
    def task(self): # a task can be hooked to the module
        while True:
            yield self.wait(2) # wait for 2 clock cycles
            print(f'Time is {self.time}')
```


```python
u_top = top()

trace = Trace()
for i in range(2):
    trace.add(u_top.i_rst[i])
    trace.add(u_top.o_cnt[i])
u_top.set_trace(trace)

u_top.i_rst[0] = 1
u_top.i_rst[1] = 1

u_top.run(3)

u_top.i_rst[0] = 0

u_top.run()

u_top.i_rst[1] = 0

u_top.run(5)
```

    Time is 2
    Time is 4
    Time is 6
    Time is 8



```python
trace.plot()
```

![alt text](examples/example.png)
