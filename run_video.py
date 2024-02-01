# Project Computer Science - run_video.py
# This file contains a visualization script using visualize and main.
# Then the video is saved using the visualizationparameters in
# parameters.py.
# Using this script, or any other script using visualize, requires FFMpeg.

import main
import numpy as np
from matplotlib import pyplot as plt
from parameters import *
import visualize


collect_steps = 400
collect_interval = 1
collect_range = 2
ncount = len(list(main.get_neighbourhood(0, 0, collect_range))) + 1
neighbourdata = np.zeros(shape=(collect_steps, ncount), dtype=int)


main.SIZE_X = 120
main.SIZE_Y = 120

# Prepare simulation using modified parameters.
sim = main.Simulation(
    fish_vision=FISH_VISION,
    shark_vision=2,
    fish_randomness=FISH_RANDOMNESS,
    cohesion_strength=COHESION_STRENGTH,
    shark_factor=SHARK_FACTOR,
    food_attraction=FOOD_ATTRACTION,
    obstacle_factor=OBSTACLE_FACTOR,
    shark_speed=SHARK_SPEED,
    food_per_step=1,
    fish_reinforcement_chance=FISH_REINFORCEMENT_CHANCE,
    daytime_duration=DAYTIME_DURATION,
    nighttime_duration=NIGHTTIME_DURATION,
    daytime_bonus=2
)

visualize.init(main.SIZE_X, main.SIZE_Y)
sim.simulate(collect_steps * collect_interval, [visualize.visualize],
             [collect_interval], FOOD_START_COUNT, [4, 5, FISH_START_CHANCE], [], 9)

visualize.finish()
