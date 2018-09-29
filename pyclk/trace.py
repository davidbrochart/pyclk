class Trace:
    def __init__(self, from_time=0, to_time=0):
        self._traces = []
        self._signals = []
        self.from_time = from_time
        self.to_time = to_time
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
        plt.style.use('dark_background')
        fig, ax = plt.subplots(len(self._traces), sharex=True)
        if len(self._signals) == 1:
            ax = [ax]
        if figsize is None:
            figsize = (15, 1 * len(self._traces))
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
            ax[i].plot(x, y, lw=0.5, antialiased=None, snap=True, color='lime')
            ax[i].yaxis.label.set_color('orange')
            c = ['slateblue', 'darkviolet'][i % 2]
            p = (i % 2) * 10
            ax[i].tick_params(axis='y', colors=c, pad=p)
            if full_path:
                ax[i].set_ylabel(path, rotation=0, color='y')
            else:
                ax[i].set_ylabel(path[path.rfind('.') + 1:], rotation=0, color='y')
        plt.show()
