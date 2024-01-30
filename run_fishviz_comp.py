# Project Computer Science - run_fishviz_comp.py
# This file contains one of a few scripts that are used to generate
# figures for the poster and report.
# This file plots the fish clustering distribution for a few
# values of the fish vision parameter.

import main
import numpy as np
from matplotlib import pyplot as plt
from parameters import *

task = int(input("task? 0 for save to file, 1 for plot from file, 2 for both.\n> "))

main.SIZE_X = GRID_X
main.SIZE_Y = GRID_Y

# Larger font size
# plt.rcParams['font.size']
plt.rcParams.update({'font.size': 15})

start_offset = 400
collect_steps = 500
collect_interval = 1
collect_range = 2
ncount = len(list(main.get_neighbourhood(0, 0, collect_range))) + 1
neighbourdata = np.empty(shape=(collect_steps, ncount), dtype=int)

runs = 30
collected_data = np.zeros(shape=(runs, ncount), dtype=int)

sim = None

if task == 0 or task == 2:
    # Prepare simulation using default parameters.
    sim = main.Simulation(
        fish_vision=FISH_VISION,
        shark_vision=SHARK_VISION,
        fish_randomness=FISH_RANDOMNESS,
        cohesion_strength=COHESION_STRENGTH,
        shark_factor=SHARK_FACTOR,
        food_attraction=FOOD_ATTRACTION,
        obstacle_factor=OBSTACLE_FACTOR,
        shark_speed=SHARK_SPEED,
        food_per_step=FOOD_PER_STEP,
        fish_reinforcement_chance=FISH_REINFORCEMENT_CHANCE,
        daytime_duration=DAYTIME_DURATION,
        nighttime_duration=NIGHTTIME_DURATION,
        daytime_bonus=DAYTIME_VISION_BONUS
    )

for vision in [2,4,6]:

    if task == 0 or task == 2:
        print(f"Simulating with {vision} fish vision per step")

        # Simulate runs.
        sim.fish_vision = vision
        for i in range(runs):
            neighbourdata.fill(0)
            sim.simulate(start_offset + collect_steps * collect_interval, [main.collect_data(collect_range, neighbourdata, start_offset)], [
                        collect_interval], FOOD_START_COUNT, [FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE], [], SHARK_START_COUNT)
            collected_data[i] = np.sum(neighbourdata, axis=0)
            print(f"Run {i} complete")

        # Compile and plot data.
        collected_data = collected_data / np.sum(collected_data, axis=1)[:, None]
        np.savetxt(f"data/fishvision={vision}.csv", collected_data, delimiter=',')

    if task == 1:
        collected_data = np.genfromtxt(f"data/fishvision={vision}.csv", delimiter=',')

    if task == 1 or task == 2:
        parts = plt.violinplot(100 * collected_data, widths=0.7, showmedians=True,
                       showextrema=True, positions=np.arange(ncount))
        

        for pc in parts['bodies']:
            pc.set_facecolor('purple')
            pc.set_alpha(1)
        parts['cmedians'].set_color('gold')
        parts['cmins'].set_color('black')
        parts['cbars'].set_alpha(0)
        parts['cmaxes'].set_color('black')

        plt.xticks(np.arange(ncount))
        plt.title(
            f"Tuna distribution among {runs} simulations of {collect_steps * collect_interval} steps.")
        plt.xlabel("Neighbour count")
        plt.xlim((-0.5, ncount-0.5))
        plt.ylabel("Tuna population (%)")
        plt.savefig(f"violin-fishvision={vision}.svg",
                    transparent=True, format="svg", bbox_inches="tight")
        plt.clf()
