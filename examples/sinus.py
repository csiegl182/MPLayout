from MPLayout.Figure import Layouter, GridLayout
import numpy as np

gl = GridLayout(
    x_min=0.15,
    y_min=0.15
)

def plot_sinus(ax):
    t = np.linspace(0, 0.1, 500)
    y = np.sin(2*np.pi*50*t)
    ax.plot(t, y)
    ax.set_xlim(0, 0.1)
    ax.set_ylim(-1.2, 1.2)
    
    ax.grid('on')
    ax.set_xlabel('$t\\rightarrow$')
    ax.set_ylabel('$\\sin(2\\pi\\cdot 50 \\mathrm{Hz}\\cdot t)\\rightarrow$')

fig = Layouter(grid_layout=gl)
fig.apply(plot_sinus)

