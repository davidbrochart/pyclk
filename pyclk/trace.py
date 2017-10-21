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
