import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from random import randrange
from parameters import GRID_X, GRID_Y, GRID_MODE

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Movie Test', artist='Matplotlib',
                comment='a red circle following a blue sine wave')
writer = FFMpegWriter(fps=15, metadata=metadata)

fig = plt.figure(facecolor='black', frameon=False, figsize=((GRID_X + 0.5) / 5, GRID_Y / 5))
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
ax = fig.add_subplot(111)
ax.set_xlim(0, GRID_X + 0.5)
ax.set_ylim(0, GRID_Y)
ax.set_facecolor("black")

frames = 200

count = min(GRID_X, GRID_Y) - frames

x, y = np.arange(0,GRID_X), np.arange(0,GRID_Y)
xv, yv = np.meshgrid(x, y)
xv = xv + (yv % 2) / 2 + 0.5
yv = yv + 0.5
colormap = ["black"] * (GRID_X * GRID_Y)

red_circle = ax.scatter(xv, yv, s=40, marker='o', c=colormap)

# Update the frames for the movie
with writer.saving(fig, "writer_test.mp4", 100):
    for i in range(frames):

        colormap[randrange(0, GRID_X * GRID_Y)] = "red"        
        # red_circle.set_data(x, y)
        red_circle.set_color(colormap)
        writer.grab_frame()
