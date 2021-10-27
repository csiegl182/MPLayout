import matplotlib
import matplotlib.pyplot as mpl
from dataclasses import dataclass
from typing import Callable, List
import os
import numpy

def get_mplstyle_path(style: str):
    return os.path.join('src', 'MPLayout', 'mplstyles', style + '.mplstyle')

def new_figure(style: str = 'default', num: int = 1, clear: bool = True, **kwargs):
    matplotlib.style.use(get_mplstyle_path(style))
    fig, ax = mpl.subplots(num=num, clear=clear, **kwargs)
    fig.show()
    return fig, ax

##
def change_ax_position(ax:mpl.axes, new_position:float, index:int):
    position = list(ax.get_position().bounds)
    position[index] = new_position
    ax.set_position(position)

def set_axes_left_offset(ax:mpl.axes, offset:float):
    change_ax_position(ax, offset, 0)

def set_axes_lower_offset(ax:mpl.axes, offset:float):
    change_ax_position(ax, offset, 1)

def set_axes_width(ax:mpl.axes, width:float):
    change_ax_position(ax, width, 2)

def set_axes_height(ax:mpl.axes, height:float):
    change_ax_position(ax, height, 3)

def get_axes_left_offset(ax:mpl.axes) -> float:
    return ax.get_position().bounds[0]

def get_axes_lower_offset(ax:mpl.axes) -> float:
    return ax.get_position().bounds[1]

def align_axes(axes:List[mpl.axes], lower_limit:float, upper_limit:float, gap:float, set_axes_size:Callable[[mpl.axes], None], get_axes_offset:Callable[[mpl.axes], float], set_axes_offset:Callable[[mpl.axes, float], None]):
    def sort_axes(axes:List[mpl.axes], get_axes_offset:Callable[[mpl.axes], float]) -> List[mpl.axes]:
        offsets = [get_axes_offset(ax) for ax in axes]
        offsets_axes = list(zip(offsets, axes))
        offsets_axes.sort(key=lambda x: x[0])
        sorted_axes = [x[1] for x in offsets_axes]
        return sorted_axes

    num_axes = len(axes)
    total_size = upper_limit - lower_limit
    sum_gaps = (num_axes - 1) * gap
    axes_size = (total_size-sum_gaps)/num_axes
    for ax in axes: set_axes_size(ax, axes_size)

    axes = sort_axes(axes, get_axes_offset)
    offsets = numpy.arange(lower_limit, upper_limit, axes_size+gap)
    for ax, offset in zip(axes, offsets): set_axes_offset(ax, offset)

@dataclass
class GridLayout:   
    x_min: float = 0.1
    x_max: float = 0.9
    y_min: float = 0.1
    y_max: float = 0.9
    x_gap: float = 0.05
    y_gap: float = 0.05
    
def vertical_align_axes(axes:List[mpl.axes], grid_layout: GridLayout = GridLayout()):
    align_axes(
        axes=axes,
        lower_limit=grid_layout.y_min,
        upper_limit=grid_layout.y_max,
        gap=grid_layout.y_gap,
        set_axes_size=set_axes_height,
        get_axes_offset=get_axes_lower_offset,
        set_axes_offset=set_axes_lower_offset)

def horizontal_align_axes(axes:List[mpl.axes], grid_layout: GridLayout = GridLayout()):
    align_axes(
        axes=axes,
        lower_limit=grid_layout.x_min,
        upper_limit=grid_layout.x_max,
        gap=grid_layout.x_gap,
        set_axes_size=set_axes_width,
        get_axes_offset=get_axes_left_offset,
        set_axes_offset=set_axes_left_offset)

class Layouter:
    def __init__(self, nrows=1, ncols=1, num: int = 1, grid_layout: GridLayout = GridLayout(), style: str = 'default', **subplot_args):
        self.grid_layout = grid_layout
        self.fig, self.axes = new_figure(num=num, nrows=nrows, ncols=ncols, style=style, **subplot_args)
        if nrows == 1 and ncols == 1:
            self.axes = numpy.array(self.axes, ndmin=2)
        else:
            self.axes.reshape((nrows, ncols))
        for row in range(nrows):
            horizontal_align_axes(self.axes[row,:], grid_layout)        
        for col in range(ncols):
            vertical_align_axes(self.axes[:,col], grid_layout)

    def layout(self, ax_fn: Callable[[mpl.axes], None], row=0, col=0):
        ax_fn(self.axes[row, col])

    def layout_all(self, ax_fn: Callable[[mpl.axes], None]):
        for ax in self.axes.flatten(): ax_fn(ax)

    def layout_row(self, ax_fn: Callable[[mpl.axes], None], row=0):
        for ax in self.axes[row,:]: ax_fn(ax)

    def layout_col(self, ax_fn: Callable[[mpl.axes], None], col=0):
        for ax in self.axes[:,col]: ax_fn(ax)

class Pool:
    def __init__(self, size: int = 1, grid_layout: GridLayout = GridLayout(), style: str = 'default', **subplot_args):
        self.figures = [Layouter(num=i, grid_layout=grid_layout, style=style, **subplot_args) for i in range(1, size+1)]

    def arange(self, begin_with: int = 1):
        pass

    def __getitem__(self, key: int):
        return self.figures[key]
