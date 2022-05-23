import matplotlib
import matplotlib.pyplot as mpl
import MPLayout.Viewports as vp
from dataclasses import dataclass
from typing import Callable, List
import os
import numpy
import pkg_resources
import inspect

def get_mplstyle_path(style: str):
    return pkg_resources.resource_filename('MPLayout', os.path.join('mplstyles', style + '.mplstyle'))

def new_figure(style: str = 'default', num: int = 1, clear: bool = True, xkcd: bool = False, **kwargs):
    if num == 1:
        matplotlib.pyplot.close('all')
    else:
        matplotlib.pyplot.close(num)
    matplotlib.style.use(get_mplstyle_path(style))
    if xkcd:
        matplotlib.rcParams['text.usetex'] = False
        with matplotlib.pyplot.xkcd():
            fig, ax = mpl.subplots(num=num, clear=clear, **kwargs)
    else:
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

def scale_axes_y(axes:List[mpl.axes], ax_ref:mpl.axes):
    pos_ref = ax_ref.get_position().bounds
    for ax in axes:
        pos = ax.get_position().bounds
        ax.set_position([pos[0], pos[1], pos[2]*pos_ref[3]/pos[3], pos_ref[3]])

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

def get_caller_filename():
    caller_stack_filenames = [stack.filename for stack in inspect.stack()]
    cwd = os.path.abspath(os.curdir)
    filename = [filename for filename in caller_stack_filenames if filename.startswith(cwd)][-1]
    return os.path.abspath(filename)

class Layouter:
    def __init__(self, nrows=1, ncols=1, num: int = 1, grid_layout: GridLayout = GridLayout(), style: str = 'default', viewport = vp.normal, xkcd: bool = False, **subplot_args):
        self.grid_layout = grid_layout
        self.num = num
        self.fig, self.axes = new_figure(num=self.num, nrows=nrows, ncols=ncols, style=style, xkcd=xkcd, **subplot_args)
        viewport(self.fig)
        if nrows == 1 and ncols == 1:
            self.axes = numpy.array(self.axes, ndmin=2)
        else:
            self.axes = self.axes.reshape((nrows, ncols))
        for row in range(nrows):
            horizontal_align_axes(self.axes[row,:], grid_layout)        
        for col in range(ncols):
            vertical_align_axes(self.axes[:,col], grid_layout)

    def apply(self, ax_fn: Callable[[mpl.axes], None], row=0, col=0):
        ax_fn(self.axes[row, col])

    def apply_all(self, ax_fn: Callable[[mpl.axes], None]):
        for ax in self.axes.flatten(): ax_fn(ax)

    def apply_row(self, ax_fn: Callable[[mpl.axes], None], row=0):
        for ax in self.axes[row,:]: ax_fn(ax)

    def apply_col(self, ax_fn: Callable[[mpl.axes], None], col=0):
        for ax in self.axes[:,col]: ax_fn(ax)

    def save(self, filename=None, rel_path='../pics', suffix='', file_type='svg'):
        if filename == None:
            filename = get_caller_filename()
        path, filename = os.path.split(filename)
        picture_name, _ = os.path.splitext(filename)
        picture_name += suffix
        picture_name += '.'+file_type
        picture_path = os.path.join(path, rel_path)
        target_file = os.path.join(picture_path, picture_name)
        self.fig.savefig(target_file)

def layout_portrait(**kwargs):
    layout = Layouter(**kwargs)
    layout.fig.set_size_inches([5.5, 8])
    return layout

def layout_landscape(**kwargs):
    layout = Layouter(**kwargs)
    layout.fig.set_size_inches([16, 4])
    return layout

def layout_1x2_normal_square(**kwargs):
    layout = Layouter(
        ncols=2,
        sharey=True,
        **kwargs)
    ax = layout.axes.flatten()
    scale_axes_y(ax[1:], ax[0])
    return layout

class Pool:
    def __init__(self, size: int = 1, grid_layout: GridLayout = GridLayout(), style: str = 'default', **subplot_args):
        self.layouts = [Layouter(num=i, grid_layout=grid_layout, style=style, **subplot_args) for i in range(1, size+1)]

    def arange(self, begin_with: int = 1):
        pass

    def apply(self, ax_fn: Callable[[mpl.axes], None]):
        for layout in self.layouts:
            layout.apply_all(ax_fn)

    def save(self, filename=None, rel_path='../pics', file_type='svg'):
        for i, layout in enumerate(self.layouts):
            layout.save(
                filename=filename,
                rel_path=rel_path,
                suffix=f'_{i+1}',
                file_type=file_type
            )

    def __getitem__(self, key: int):
        return self.layouts[key-1]

