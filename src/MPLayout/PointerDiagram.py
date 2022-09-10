from MPLayout.Figure import layout_square
from MPLayout.Elements import arrow
from MPLayout.Style import color
import numpy as np

class PointerDiagram:
    colormap = {
        'k' : color.black,
        'b' : color.blue,
        'r' : color.red,
        'g' : color.green,
        'gray' : color.grey
    }
    def __init__(self, layout=layout_square, **kwargs):
        self.layout = layout(**kwargs)
        self.fig = self.layout.fig
        self.ax = self.layout.axes[0][0]
        self.ax.grid('on')

    def pointer(self, *args, z0=0, scale=1, color=color.black):
        for z in args:
            z *= scale
            arrow(self.ax, [np.real(z0), np.imag(z0)], [np.real(z)+np.real(z0), np.imag(z)+np.imag(z0)], color=self.colormap.get(color, color))
        return self

    def show(self):
        pass

class VoltagePointerDiagram(PointerDiagram):
    def __init__(self, res=1, **kwargs):
        super().__init__(**kwargs)
        self.res = res

    def voltage(self, *args, u0=0, color=color.blue):
        return self.pointer(*args, z0=u0, color=color)

    def current(self, *args, i0=0, color=color.red):
        p = (i*self.res for i in args)
        return self.pointer(*p, z0=i0*self.res, color=color)

class CurrentPointerDiagram(PointerDiagram):
    def __init__(self, res=1, **kwargs):
        super().__init__(**kwargs)
        self.res = res

    def voltage(self, *args, u0=0, color=color.blue):
        p = (u/self.res for u in args)
        return self.pointer(*p, z0=u0/self.res, color=color)

    def current(self, *args, i0=0, color=color.red):
        return self.pointer(*args, z0=i0, color=color)