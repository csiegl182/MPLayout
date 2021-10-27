import matplotlib.pyplot
import matplotlib.patches as ptch
import numpy
import os
import inspect

##
matplotlib.pyplot.rcParams['font.size'] = 14
matplotlib.pyplot.rcParams['font.serif'] = 'Computer Modern Roman'
matplotlib.pyplot.rcParams['text.usetex'] = True
matplotlib.pyplot.rcParams['svg.fonttype'] = 'none'
matplotlib.pyplot.rcParams['figure.figsize'] = (9.0, 4.5)
matplotlib.pyplot.rcParams['lines.linewidth'] = 3
matplotlib.pyplot.rcParams['lines.markeredgewidth'] = 0
matplotlib.pyplot.rcParams['lines.markersize'] = 15
matplotlib.rcParams['axes.axisbelow'] = True

##
class color:
    black = (0,0,0)
    grey = (.7, .7, .7)
    lightgrey = (.9, .9, .9)
    darkgrey = (.5, .5, .5)
    darkblue = (.13, .22, .39)
    lightblue = (.4, .7, 1)
    red = (1, .3, 0)
    green = (0, .7, 0)
    blue = (.18, .33, .59)
    purple = (.44, .19, .63)

##
def arrow_head(xy_tip, height, width, direction='right', angle=None, color=color.black, gid=''):
    A = lambda phi: numpy.matrix([[numpy.cos(phi), -numpy.sin(phi)], [numpy.sin(phi), numpy.cos(phi)]])
    if angle == None:
        if direction == 'up':
            S = A(numpy.pi/2)
        elif direction == 'left':
            S = A(numpy.pi)
        elif direction == 'down':
            S = A(-numpy.pi/2)
        else:
            S = A(0)
    else:
        S = A(angle)

    x_tip = xy_tip[0]
    y_tip = xy_tip[1]
    p0 = numpy.matrix([[x_tip], [y_tip]])
    x = numpy.array([x_tip, x_tip-height, x_tip-height, x_tip])
    y = numpy.array([y_tip, y_tip-width/2, y_tip+width/2, y_tip])
    p = numpy.matrix([x, y])

    p_rot = S*(p-p0) + p0
    x_rot = numpy.array(p_rot[0][:]).flatten()
    y_rot= numpy.array(p_rot[1][:]).flatten()
    return ptch.Polygon([*zip(x_rot, y_rot)], color=color, linewidth=0, gid=gid, zorder=100)

def cursor(x, y, r=0.06, color=color.black, gid=''):
    return ptch.Circle((x, y), r, color=color, gid=gid, clip_on=False, zorder=100)

##
def vertical_align_axes(axes_vec, y_pos_max=0.95, y_pos_min=0.12, y_gap=0.05):
    num_axes = len(axes_vec)
    total_height = y_pos_max-y_pos_min
    gaps_height = (num_axes-1)*y_gap
    ax_height = (total_height-gaps_height)/num_axes
    set_ax_height = lambda ax: change_ax_position(ax=ax, new_position=ax_height, index=3)
    [set_ax_height(ax) for ax in axes_vec]

    y_offsets = [a.get_position().bounds[1] for a in axes_vec]
    yoffsets_ax = list(zip(y_offsets, axes_vec))
    yoffsets_ax.sort(key=lambda x: x[0])
    axes_vec = [x[1] for x in yoffsets_ax]
    y_offsets = numpy.arange(y_pos_min, y_pos_max, ax_height+y_gap)
    set_ax_offsets = lambda ax, offset: change_ax_position(ax=ax, new_position=offset, index=1)
    [set_ax_offsets(a, y) for a, y in zip(axes_vec, y_offsets)]

def horizontal_align_axes(axes_vec, x_pos_max=0.95, x_pos_min=0.12, x_gap=0.05):
    num_axes = len(axes_vec)
    total_width = x_pos_max-x_pos_min
    gaps_width = (num_axes-1)*x_gap
    ax_width = (total_width-gaps_width)/num_axes
    set_ax_width = lambda ax: change_ax_position(ax=ax, new_position=ax_width, index=2)
    [set_ax_width(ax) for ax in axes_vec]

    x_offsets = [a.get_position().bounds[1] for a in axes_vec]
    xoffsets_ax = list(zip(x_offsets, axes_vec))
    xoffsets_ax.sort(key=lambda x: x[0])
    axes_vec = [x[1] for x in xoffsets_ax]
    x_offsets = numpy.arange(x_pos_min, x_pos_max, ax_width+x_gap)
    set_ax_offsets = lambda ax, offset: change_ax_position(ax=ax, new_position=offset, index=0)
    [set_ax_offsets(a, y) for a, y in zip(axes_vec, x_offsets)]

def change_ax_position(ax, new_position, index):
    position = list(ax.get_position().bounds)
    position[index] = new_position
    ax.set_position(position)

def align_figure1x1(fig, y_pos_max=0.95, y_pos_min=0.12, y_gap=0.05):
    vertical_align_axes(
        fig.get_axes(),
        y_pos_max=y_pos_max,
        y_pos_min=y_pos_min,
        y_gap=y_gap)

def align_figure2x1(fig, y_pos_max=0.95, y_pos_min=0.05, y_gap=0.05):
    vertical_align_axes(fig.get_axes(), y_pos_max=y_pos_max, y_pos_min=y_pos_min, y_gap=y_gap)
    fig.align_ylabels()

def align_figure1x2_wide(fig):
    fig.set_size_inches((15, 3))
    ax = fig.get_axes()
    horizontal_align_axes(ax, x_pos_min=0.05, x_gap=0.08)
    for a in ax:
        vertical_align_axes([a], y_pos_min=0.16)

def save_picture(fig, file_type='svg'):
    def get_target_file(prefix=''):
        filename = inspect.stack()[2].filename
        path, filename = os.path.split(os.path.abspath(filename))
        picture_name, _ = os.path.splitext(filename)
        picture_name += prefix
        picture_name += '.'+file_type
        picture_path = path.split(os.sep)[:-1] + ['pics']
        picture_path = os.sep.join(picture_path)
        return os.path.join(picture_path, picture_name)
    if isinstance(fig, list):
        target_file = []
        for i, f in enumerate(fig):
            target_file.append(get_target_file('_{}'.format(i+1)))
            f.savefig(target_file[-1])
    else:
        target_file = get_target_file()
        fig.savefig(target_file)
    return target_file