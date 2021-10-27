import numpy
import matplotlib.patches as ptch
from PlottingExtensions import Style as sty

def get_aspect(ax):
    figW, figH = ax.get_figure().get_size_inches()
    _, _, w, h = ax.get_position().bounds
    disp_ratio = (figH * h) / (figW * w)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    data_ratio = (ylim[1]-ylim[0]) / (xlim[1]-xlim[0])
    return disp_ratio / data_ratio

##
def polygon(ax, x, y, facecolor=sty.color.lightgrey, edgecolor=sty.color.darkgrey, **kwargs):
    poly = ptch.Polygon([*zip(x,y)], facecolor=facecolor, edgecolor=edgecolor, **kwargs)
    ax.add_patch(poly)
    
def arrow_head(ax, xy_tip, height, width, direction='up', angle=None, color=sty.color.black, gid='', **kwargs):
    def A(phi, r):
        return numpy.matrix([[numpy.cos(phi)   , -numpy.sin(phi)*r],
                             [numpy.sin(phi)/r ,  numpy.cos(phi)  ]])

    def arrow_polygon(xy_tip, heigth, width, angle, xy_aspect):
        p_tip = numpy.matrix([[xy_tip[0]], [xy_tip[1]]])
        p = numpy.matrix([numpy.array([-height, 0, -height]),
                          numpy.array([width/2, 0, -width/2])])
        return A(angle, xy_aspect)*p + p_tip

    def get_patch(polygon, color, gid, **kwargs):
        x = numpy.array(polygon[0][:]).flatten()
        y = numpy.array(polygon[1][:]).flatten()
        if 'linewidth' in kwargs.keys(): kwargs.pop('linewidth')
        return ptch.Polygon([*zip(x, y)], color=color, linewidth=0, gid=gid, **kwargs)

    def get_angle(direction):
        if direction == 'up':
            return numpy.pi/2
        elif direction == 'left':
            return numpy.pi
        elif direction == 'down':
            return -numpy.pi/2
        else:
            return 0

    if angle == None: angle = get_angle(direction)
    polygon = arrow_polygon(xy_tip, height, width, angle, get_aspect(ax))
    patch = get_patch(polygon, color, gid, **kwargs)
    ax.add_patch(patch)

def arrow(ax, xy0, xy1, rel_height=0.15, rel_width=0.13, color=sty.color.black, gid='', **kwargs):
    dx = xy1[0]-xy0[0]
    dy = xy1[1]-xy0[1]
    length = numpy.sqrt(dx**2 + dy**2)
    angle = numpy.arctan2(dy, dx)
    arrow_head(
        ax=ax,
        xy_tip=xy1,
        height=rel_height*length,
        width=rel_width*length,
        angle=angle,
        color=color,
        gid=gid+'_head',
        **kwargs)

    base_length = (1-rel_height)*length
    base_dx = base_length*numpy.cos(angle)
    base_dy = base_length*numpy.sin(angle)
    ax.plot([xy0[0], xy0[0]+base_dx], [xy0[1], xy0[1]+base_dy], color=color, gid=gid+'_base', **kwargs)

def cursor(ax, xy, r=1, color=sty.color.black, gid=''):
    patch = ptch.Ellipse(xy, r, r/get_aspect(ax), color=color, gid=gid, clip_on=False, zorder=100)
    ax.add_patch(patch) 

def coordinate_system(ax, x_arrow_length=0.05, x_arrow_base=0.1, neg_arrow=True, gid_ext=''):
    def move_spines(ax, xlim, ylim, arrow_length):
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_gid('x_axis{:s}'.format(gid_ext))
        ax.spines['left'].set_gid('y_axis{:s}'.format(gid_ext))
        if xlim[0] < 0:
            ax.spines['bottom'].set_bounds(xlim[0]+arrow_length, xlim[1]-arrow_length)
        else:
            ax.spines['bottom'].set_bounds(0, xlim[1]-arrow_length)
        if ylim[0] < 0:
            ax.spines['left'].set_bounds(ylim[0]+arrow_length/get_aspect(ax), ylim[1]-arrow_length/get_aspect(ax))
        else:
            ax.spines['left'].set_bounds(0, ylim[1]-arrow_length/get_aspect(ax))

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    if xlim[0] > 0:
        xlim[0] = 0
        ax.set_xlim(xlim)
    if ylim[0] > 0:
        ylim[0] = 0
        ax.set_ylim(ylim)
    width = xlim[1]-xlim[0]

    arrow_height = width*x_arrow_length
    arrow_width = width*x_arrow_base

    move_spines(ax, xlim, ylim, arrow_height)
    arrow_head(ax, (xlim[1], 0), arrow_height, arrow_width, direction='right', clip_on=False, gid='x_axis_pos_head{:s}'.format(gid_ext))
    arrow_head(ax, (0, ylim[1]), arrow_height, arrow_width, direction='up', clip_on=False, gid='y_axis_pos_head{:s}'.format(gid_ext))
    if xlim[0] < 0 and neg_arrow:
        arrow_head(ax, (xlim[0], 0), arrow_height, arrow_width, direction='left', clip_on=False, gid='x_axis_neg_head{:s}'.format(gid_ext))
    if ylim[0] < 0 and neg_arrow:
        arrow_head(ax, (0, ylim[0]), arrow_height, arrow_width, direction='down', clip_on=False, gid='y_axis_neg_head{:s}'.format(gid_ext))

def horizontal_legend(ax, **kwargs):
    ax.legend(
        bbox_to_anchor=(0., 1.02, 1., .102),
        loc='lower center',
        ncol=len(ax.get_legend_handles_labels()[0]),
        borderaxespad=0.,
        frameon=False,
        **kwargs
        )
