from matplotlib import scale
import numpy
import itertools
import matplotlib.patches as ptch
import MPLayout.Style as sty

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

def circle(ax, x0=0, y0=0, r=1, n=50, fill=False, **kwargs):
    phi = numpy.linspace(0, 2*numpy.pi*(n+1)/n, n+1)
    x = r*numpy.cos(phi)*get_aspect(ax)+x0
    y = r*numpy.sin(phi)+y0
    h = ax.plot(x,  y, **kwargs)
    if fill:
        polygon(ax, x, y, facecolor=sty.color.white, edgecolor=sty.color.white, zorder=h[0].zorder-1)

def minus(ax, x0=0, y0=0, r=0.2, n=20, color=sty.color.black, fill=False, **kwargs):
    circle(ax, x0=x0, y0=y0, r=r, n=n, color=color, fill=fill, **kwargs)
    ax.plot([x0-0.5*r*get_aspect(ax), x0+0.5*r*get_aspect(ax)], [y0, y0], color=color, **kwargs)

def plus(ax, x0=0, y0=0, r=0.2, n=20, color=sty.color.black, fill=False, **kwargs):
    minus(ax, x0=x0, y0=y0, r=r, n=n, color=color, fill=fill, **kwargs)
    ax.plot([x0, x0], [y0-0.5*r, y0+0.5*r], color=color, **kwargs)

def z_arrow(ax, x, y, z_dir=1, diameter=0.1, color=sty.color.black, **kwargs):
    radius = diameter/2
    circle = ptch.Circle((x, y), radius, edgecolor=color, facecolor=sty.color.white, **kwargs)
    ax.add_patch(circle)
    if z_dir == 0:
        pass
    elif z_dir > 0:
        dot = ptch.Circle((x, y), radius/10, edgecolor=color, facecolor=sty.color.black, **kwargs)
        ax.add_patch(dot)
    else:
        delta = numpy.sqrt(2)/2*radius
        ax.plot((x-delta, x+delta), (y-delta, y+delta), color=color, **kwargs)
        ax.plot((x-delta, x+delta), (y+delta, y-delta), color=color, **kwargs)

def arrow_head(ax, xy0, height, width, direction='up', angle=None, pivot='top', color=sty.color.black, gid='', **kwargs):
    def A(phi, xy_ratio):
        return numpy.matrix([[numpy.cos(phi)   , -numpy.sin(phi)*xy_ratio],
                             [numpy.sin(phi)/xy_ratio ,  numpy.cos(phi)  ]])

    def triangular_top(xy0, height, width):
        p0 = numpy.matrix([[xy0[0]], [xy0[1]]])
        p = numpy.matrix([numpy.array([-height, 0, -height]),
                          numpy.array([width/2, 0, -width/2])])
        return p0, p

    def triangular_center(xy0, height, width):
        p0 = numpy.matrix([[xy0[0]], [xy0[1]]])
        p = numpy.matrix([numpy.array([-height/3, 2/3*height, -height/3]),
                          numpy.array([width/2, 0, -width/2])])
        return p0, p
    
    triangular_polygon = {
        'top': triangular_top,
        'center': triangular_center,
    }

    def rotate_arrow(p0, p, angle, xy_aspect):
        return A(angle, xy_aspect)*p + p0

    def get_patch(polygon, color, gid, **kwargs):
        x = numpy.array(polygon[0][:]).flatten()
        y = numpy.array(polygon[1][:]).flatten()
        if 'linewidth' in kwargs.keys(): kwargs.pop('linewidth')
        return ptch.Polygon([*zip(x, y)], color=color, linewidth=0, gid=gid, **kwargs)

    arrow_direction = {
        'right': 0,
        'up': numpy.pi/2,
        'left': numpy.pi,
        'down': -numpy.pi/2
    }

    def get_angle(direction, angle):
        if angle == None:
            angle = arrow_direction.get(direction, direction)
        return angle

    p0, p = triangular_polygon[pivot](xy0, height, width)
    polygon = rotate_arrow(p0, p, get_angle(direction, angle), get_aspect(ax))
    patch = get_patch(polygon, color, gid, **kwargs)
    ax.add_patch(patch)

def arrow(ax, xy0, xy1, height=None, width=None, tail=False, color=sty.color.black, gid='', **kwargs):
    dx = xy1[0]-xy0[0]
    dy = xy1[1]-xy0[1]
    length = numpy.sqrt(dx**2 + dy**2)
    alpha_r = numpy.arctan2(dy*get_aspect(ax), dx)
    alpha = numpy.arctan2(dy, dx)
    if height is None:
        height = 0.15*length
    if width is None:
        width = 3/4*height
    arrow_head(
        ax=ax,
        xy0=xy1,
        height=height,
        width=width,
        angle=alpha_r,
        color=color,
        gid=gid+'_head',
        **kwargs)
    if tail:
        arrow_head(
            ax=ax,
            xy0=xy0,
            height=height,
            width=width,
            angle=alpha-numpy.pi,
            color=color,
            gid=gid+'_tail',
            **kwargs)

    if get_aspect(ax) > 1:
        aspect = get_aspect(ax)
    else:
        aspect = 1
    if tail:
        xy0[0]+=height*numpy.cos(alpha)/aspect
        xy0[1]+=height*numpy.sin(alpha)/aspect
    xy1[0]-=height*numpy.cos(alpha)/aspect
    xy1[1]-=height*numpy.sin(alpha)/aspect

    ax.plot([xy0[0], xy1[0]], [xy0[1], xy1[1]], color=color, gid=gid+'_base', **kwargs)

def complex_pointer(ax, z0, z1, **kwargs):
    arrow(ax, (numpy.real(z0), numpy.imag(z0)), (numpy.real(z1), numpy.imag(z1)), **kwargs)

def cursor(ax, xy, r=1, color=sty.color.black, gid=''):
    patch = ptch.Ellipse(xy, r, r/get_aspect(ax), color=color, gid=gid, clip_on=False, zorder=100)
    ax.add_patch(patch) 

def vector_field(ax, vec_fcn, x_start, x_end, delta_x, y_start, y_end, delta_y, length_scale=0.8, height=None, width=None, **kwargs):
    xvec = numpy.arange(x_start, x_end+delta_x, delta_x)
    yvec = numpy.arange(y_start, y_end+delta_y, delta_y)

    fmax_x = numpy.max([vec_fcn(x,y)[0] for x, y in itertools.product(xvec, yvec)])
    fmax_y = numpy.max([vec_fcn(x,y)[1] for x, y in itertools.product(xvec, yvec)])

    f0 = numpy.sqrt((fmax_x/delta_x)**2 + (fmax_y/delta_y)**2)/length_scale

    if height == None:
        height = delta_x/7
    if width == None:
        width = delta_y/7

    for x, y in itertools.product(xvec, yvec):
        arrow(ax, (x, y), numpy.array([x, y])+ vec_fcn(x, y)/f0, height=height, width=width, **kwargs)

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
    arrow_head(ax, (xlim[1], 0), arrow_height, arrow_width, direction='right', clip_on=False, gid='x_axis_pos_head{:s}'.format(gid_ext), zorder=200)
    arrow_head(ax, (0, ylim[1]), arrow_height, arrow_width, direction='up', clip_on=False, gid='y_axis_pos_head{:s}'.format(gid_ext), zorder=200)
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
