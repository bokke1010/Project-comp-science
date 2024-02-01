A project for the course "Project Computational science" for the UvA university.

Features:
A fish schooling simulation using a wrap-around hexagon grid.

Features fish swimming around in schools, eating food and getting chased
by sharks, all the while getting blocked by rocks.
Including stochastic effects and a large number of parameters to affect
different systems in the simulation.



File descriptions:
main.py
    Contains all primary grid and simulation code
parameters.py
    Contains all default parameters
visualize.py
    Contains code to create videos from simulations
Perlinnoise.py
    Contains a efficient perlin noise implementation, used by main.py
run_*_comp.py
    A collection of scripts that utilize main.py to generate figures
    Of these, run_food_comp, run_daylight_comp and run_fishviz_comp
    prompt for a task to be just a simulation, just a visualization
    or both (task = 0, 1, 2 respectively).
    All other run files run both the simulation and visualization
    consecutively, and are not used in the report or poster.
run_video.py
    A script that runs a simulation and visualizes it into "video.mp4".
    This script (and any other usage of visualize.py) requires FFMpeg to be available.

Dependencies:
Matplotlib
Numpy
FFMpeg must be available from the execution location if you want to use
visualize.py to create videos.
