import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from parameters import FPS

writer = None
circle_grid, colormap = None, None

cell_colors = ["", "black", "yellow", "red", "green"]

def init(xsize, ysize, mode):
    global writer, savefunc, circle_grid, colormap
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='a visualization')
    writer = FFMpegWriter(fps=FPS, metadata=metadata)

    fig = plt.figure(facecolor='black', frameon=False, figsize=((xsize + 0.5) / 5, ysize / 5))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, xsize + 0.5)
    ax.set_ylim(0, ysize)
    ax.set_facecolor("black")

    x, y = np.arange(0, xsize), np.arange(0, ysize)
    xv, yv = np.meshgrid(x, y)
    xv = xv + (yv % 2) / 2 + 0.5
    yv = yv + 0.5
    colormap = ["black"] * (xsize * ysize)

    circle_grid = ax.scatter(xv, yv, s=40, marker='o', c=colormap)
    writer.setup(fig, "writer_test.mp4", 100)

def visualize(grid):
    i=0
    for row in grid.grid:
        for cell in row:
            colormap[i] = cell_colors[cell.cell_type]        
            i+=1

    circle_grid.set_color(colormap)
    writer.grab_frame()

def finish():
    writer.finish()