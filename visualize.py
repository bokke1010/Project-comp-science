import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from parameters import VisualizationOptions

writer = None
circle_grid, colormap = None, None

cell_colors = ["", VisualizationOptions.BG_COLOR, "yellow", "red", "white"]

def init(xsize, ysize, mode):
    global writer, savefunc, circle_grid, colormap
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='a visualization')
    writer = FFMpegWriter(fps=VisualizationOptions.FPS, metadata=metadata)

    fig = plt.figure(
        frameon=False,
        figsize=(
            (xsize + 0.5) / VisualizationOptions.CELLS_PER_INCH,
            ysize / VisualizationOptions.CELLS_PER_INCH)
    )
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, xsize + 0.5)
    ax.set_ylim(0, ysize)
    ax.set_facecolor(VisualizationOptions.BG_COLOR)

    x, y = np.arange(0, xsize), np.arange(0, ysize)
    xv, yv = np.meshgrid(x, y)
    xv = xv + (yv % 2) / 2 + 0.5
    yv = yv + 0.5
    colormap = [VisualizationOptions.BG_COLOR] * (xsize * ysize)

    circle_grid = ax.scatter(xv, yv, s= (2 * VisualizationOptions.PIXELS_PER_ENTITY)**2, marker='o', c=colormap)
    writer.setup(fig, f"{VisualizationOptions.FILE_NAME}.mp4", VisualizationOptions.PIXELS_PER_INCH)

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