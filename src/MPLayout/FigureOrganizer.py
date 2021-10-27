import matplotlib.pyplot
import numpy
import os
import inspect

style_path = '../mplstyles'

def get_retlative_path(path):
    target_dir = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    target_dir += path.split(os.sep)
    return os.path.abspath(os.sep.join(target_dir))

def get_mplstyle_path(style, path=style_path):
    mpl_path = get_retlative_path(path)
    mpl_path = mpl_path.split(os.sep)
    mpl_path.append(style + '.mplstyle')
    return os.path.abspath(os.sep.join(mpl_path))

##
def new_figure(nrows=1, ncols=1, num=1, clear=True, plt_function=None, align_function=None, style='default', **kwargs):
    if num == 1:
        matplotlib.pyplot.close('all')
    else:
        matplotlib.pyplot.close(num)
    matplotlib.style.use(get_mplstyle_path(style))
    fig, ax = matplotlib.pyplot.subplots(nrows=nrows, ncols=ncols, num=num, clear=clear, **kwargs)
    if plt_function is not None:
        plt_function(ax)
    if align_function is not None:
        align_function(fig)
    fig.show()
    return fig

##
def vertical_align_axes(axes_vec, y_pos_max=0.95, y_pos_min=0.12, y_gap=0.05):
    num_axes = len(axes_vec)
    total_height = y_pos_max - y_pos_min
    gaps_height = (num_axes - 1) * y_gap
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

def scale_y(ax, ax_ref):
    pos_ref = ax_ref.get_position().bounds
    pos = ax.get_position().bounds
    ax.set_position([pos[0], pos[1], pos[2]*pos_ref[3]/pos[3], pos_ref[3]])

def figure1x1(fig, x_pos_min=0.01, y_pos_min=0.01, x_pos_max=0.99, y_pos_max=0.99):
    ax = fig.get_axes()[0]
    ax.set_position([x_pos_min, y_pos_min, x_pos_max-x_pos_min, y_pos_max-y_pos_min])

def figure1x1_wide(fig, **kwargs):
    fig.set_size_inches((15, 3))
    figure1x1(fig, **kwargs)

def figure1x1_square(fig, y_pos_min=0, y_pos_max=1):
    fig.set_size_inches((4.5, 4))
    vertical_align_axes(
        fig.get_axes(),
        y_pos_max=y_pos_max,
        y_pos_min=y_pos_min)

def figureNx1(fig, x_pos_min=0.08, y_pos_min=0.11, x_pos_max=0.98, y_pos_max=1.0, y_gap=0.05):
    vertical_align_axes(fig.get_axes(), y_pos_min=y_pos_min, y_pos_max=y_pos_max, y_gap=y_gap)
    for ax in fig.get_axes():
        horizontal_align_axes([ax], x_pos_min=x_pos_min, x_pos_max=x_pos_max)
    fig.align_ylabels()

def figure1xN(fig, x_pos_min=0.08, y_pos_min=0.11, x_pos_max=0.98, y_pos_max=1.0, x_gap=0.05):
    horizontal_align_axes(fig.get_axes(), x_pos_min=x_pos_min, x_pos_max=x_pos_max, x_gap=x_gap)
    for ax in fig.get_axes():
        vertical_align_axes([ax], y_pos_min=y_pos_min, y_pos_max=y_pos_max)
    fig.align_xlabels()

def figure4x4(fig, x_pos_min=0.08, y_pos_min=0.11, x_pos_max=0.98, y_pos_max=1.0, x_gap=0.05, y_gap=0.05):
    ax = fig.get_axes()
    horizontal_align_axes([ax[0], ax[1]], x_pos_min=x_pos_min, x_pos_max=x_pos_max, x_gap=x_gap)
    horizontal_align_axes([ax[2], ax[3]], x_pos_min=x_pos_min, x_pos_max=x_pos_max, x_gap=x_gap)
    vertical_align_axes([ax[0], ax[2]], y_pos_min=y_pos_min, y_pos_max=y_pos_max, y_gap=y_gap)
    vertical_align_axes([ax[1], ax[3]], y_pos_min=y_pos_min, y_pos_max=y_pos_max, y_gap=y_gap)
    fig.align_xlabels([ax[0], ax[1]])
    fig.align_xlabels([ax[2], ax[3]])
    fig.align_ylabels([ax[0], ax[2]])
    fig.align_ylabels([ax[1], ax[3]])

def figure1xN_wide(fig, **kwargs):
    fig.set_size_inches((15, 3))
    figure1xN(fig, **kwargs)

def figure1xN_semiwide(fig, **kwargs):
    fig.set_size_inches((12, 4))
    figure1xN(fig, **kwargs)

def figure2x1(fig, y_pos_max=0.95, y_pos_min=0.05, y_gap=0.05):
    vertical_align_axes(fig.get_axes(), y_pos_max=y_pos_max, y_pos_min=y_pos_min, y_gap=y_gap)
    fig.align_ylabels()

def figure1x2_wide(fig):
    fig.set_size_inches((15, 3))
    ax = fig.get_axes()
    horizontal_align_axes(ax, x_pos_min=0.05, x_gap=0.08)
    for a in ax:
        vertical_align_axes([a], y_pos_min=0.16)

def figure2x2_square_right(fig, **kwargs):
    figure2x2(fig, **kwargs)
    ax_top_left, ax_top_right, ax_bottom_left, ax_bottom_right = fig.get_axes()
    scale_y(ax_top_right, ax_top_left)
    scale_y(ax_bottom_right, ax_bottom_left)

def figure2x2(fig, x_pos_min=0.08, y_pos_min=0.11, x_pos_max=0.98, y_pos_max=1.0, x_gap=0.5, y_gap=0.05):
    ax_top_left, ax_top_right, ax_bottom_left, ax_bottom_right = fig.get_axes()
    horizontal_align_axes([ax_top_left, ax_top_right], x_pos_min=x_pos_min, x_pos_max=x_pos_max, x_gap=x_gap)
    horizontal_align_axes([ax_bottom_left, ax_bottom_right], x_pos_min=x_pos_min, x_pos_max=x_pos_max, x_gap=x_gap)
    vertical_align_axes([ax_top_left, ax_bottom_left], y_pos_min=y_pos_min, y_pos_max=y_pos_max, y_gap=y_gap)
    vertical_align_axes([ax_top_right, ax_bottom_right], y_pos_min=y_pos_min, y_pos_max=y_pos_max, y_gap=y_gap)

def save_picture(fig, filename=None, file_type='svg'):
    def get_target_file(filename=None, prefix=''):
        if filename == None:
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
            target_file.append(get_target_file(filename, '_{}'.format(i+1)))
            f.savefig(target_file[-1])
    else:
        target_file = get_target_file(filename)
        fig.savefig(target_file)
    return target_file