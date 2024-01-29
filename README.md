A project for the course "Project Computational science" for the UvA university.

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
run_video.py
    A script that runs a simulation and visualizes it into "video.mp4".
    This script (and any other usage of visualize.py) requires FFMpeg to be available.

Dependencies:
Matplotlib
Numpy
FFMpeg must be available from the execution location if you want to use visualize.py to create videos