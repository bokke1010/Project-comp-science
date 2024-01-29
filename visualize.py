# Project Computer Science - visualize.py
# This file contains code to turn a simulation into a video.
# It can be imported by other files in conjunction with main.py
# to create visualizations.
# This file expects FFMpeg to be available, so put it on your system path.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from parameters import VisualizationOptions

writer = None
circle_grid, colormap = None, None

# Colors corresponding with the cell indices in main.py
cell_colors = ["", VisualizationOptions.BG_COLOR,
               "yellow", "red", "white", "black"]


def init(xsize, ysize):
    """Initialize a visualization for a [xsize] x [ysize] grid."""
    global writer, savefunc, circle_grid, colormap
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='A PCS simulation visualization', artist='Bokke')
    writer = FFMpegWriter(fps=VisualizationOptions.FPS, metadata=metadata)

    fig = plt.figure(
        frameon=False,
        figsize=(
            (xsize + 0.5) / VisualizationOptions.CELLS_PER_INCH,
            ysize / VisualizationOptions.CELLS_PER_INCH)
    )

    # Fill the frame with the graph
    fig.subplots_adjust(left=0, bottom=0, right=1,
                        top=1, wspace=None, hspace=None)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, xsize + 0.5)
    ax.set_ylim(0, ysize)
    ax.set_facecolor(VisualizationOptions.BG_COLOR)

    # Calculate all the cell coordinates
    x, y = np.arange(0, xsize), np.arange(0, ysize)
    xv, yv = np.meshgrid(x, y)
    xv = xv + (yv % 2) / 2 + 0.5
    yv = yv + 0.5
    colormap = [VisualizationOptions.BG_COLOR] * (xsize * ysize)

    # Generate all the cell dots and initialize the video creation
    circle_grid = ax.scatter(xv, yv, s=(2 * VisualizationOptions.PIXELS_PER_ENTITY)**2,
                             marker='o', c=colormap, edgecolors=None)
    writer.setup(fig, f"{VisualizationOptions.FILE_NAME}.mp4",
                 VisualizationOptions.PIXELS_PER_INCH)


def visualize(grid, _):
    """Add a frame to the visualization based on [grid]."""
    i = 0
    for row in grid.grid:
        for cell in row:
            colormap[i] = cell_colors[cell.cell_type]
            i += 1

    circle_grid.set_color(colormap)
    writer.grab_frame()


def finish():
    """Complete the vide file."""
    writer.finish()
