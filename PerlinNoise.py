import math
import random
import numpy as np 
import matplotlib.pyplot as plt

def smoothstep(t):
   
    return t * t * (3 - 2 * t)

def lerp(a, b, t):

    return a + t * (b - a)


def generate_perlin_noise(width, height, scale):

    noise = np.zeros((height, width))

    gradients = np.random.randn(height // scale + 2, width // scale + 2, 2) 

    for y in range(height):
        for x in range(width):
            x_cell = x // scale 
            y_cell = y // scale 

            in_x_cell = x / scale - x_cell
            in_y_cell = y / scale - y_cell 

            # calculate the dot products
            dot_top_left = np.dot(gradients[y_cell, x_cell], [in_x_cell, in_y_cell])
            dot_top_right = np.dot(gradients[y_cell, x_cell + 1], [in_x_cell - 1, in_y_cell])
            dot_bottom_left = np.dot(gradients[y_cell + 1, x_cell], [in_x_cell, in_y_cell - 1])
            dot_bottom_right = np.dot(gradients[y_cell + 1, x_cell + 1], [in_x_cell - 1, in_y_cell - 1])

            # interpolating along the x axis
            interpolate_x_top = smoothstep(in_x_cell)
            interpolate_x_bottom = smoothstep(in_x_cell - 1)

            interpolated_top = lerp(dot_top_left, dot_top_right, interpolate_x_top)
            interpolated_bottom = lerp(dot_bottom_left, dot_bottom_right, interpolate_x_top)

            # interpolating along y axis
            interpolate_y = smoothstep(in_y_cell)

            # interpolating the final values
            noise[y, x] = lerp(interpolated_top, interpolated_bottom, interpolate_y)

    # normalizing 
    noise = (noise - np.min(noise)) / (np.max(noise) - np.min(noise))

    return noise


width, height = 256, 256
scale = 100
perlin_noise = generate_perlin_noise(width, height, scale)

plt.imshow(perlin_noise, cmap='viridis', interpolation='nearest')
plt.colorbar()
plt.show()








