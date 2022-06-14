import matplotlib.pyplot

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
    black = (0, 0, 0)
    grey = (.7, .7, .7)
    lightgrey = (.9, .9, .9)
    darkgrey = (.5, .5, .5)
    darkdarkgrey = (.2, .2, .2)
    darkblue = (.13, .22, .39)
    lightblue = (.4, .7, 1)
    red = (0.721, 0, 0)
    darkred = (0.8, 0, 0)
    green = (0, 0.45, 0.333)
    blue = (.18, .33, .59)
    purple = (.44, .19, .63)
    white = (1, 1, 1)