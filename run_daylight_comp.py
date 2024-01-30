# Project Computer Science - run_daylight_comp.py
# This file contains one of a few scripts that are used to generate
# figures for the poster and report.
# This file plots average fish clustering against time, highlighting
# the day/night cycle.

import main
import numpy as np
from matplotlib import pyplot as plt
from parameters import *

main.SIZE_X = GRID_X
main.SIZE_Y = GRID_Y

collect_steps = 1500
collect_interval = 1
collect_range = 2
ncount = len(list(main.get_neighbourhood(0, 0, collect_range))) + 1
neighbourdata = np.empty(shape=(collect_steps, ncount), dtype=int)

runs = 20
collected_data = np.zeros(shape=(runs, collect_steps), dtype=float)

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

# Run simulations.
for i in range(runs):
    neighbourdata.fill(0)
    sim.simulate(collect_steps * collect_interval, [main.collect_data(collect_range, neighbourdata)],
                 [collect_interval], FOOD_START_COUNT, [FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE], [], SHARK_START_COUNT)

    collected_data[i] = (neighbourdata @ np.arange(ncount)
                         ) / np.sum(neighbourdata, axis=1)
    print(f"Run {i} complete")


# Generate day lines.
day_duration = DAYTIME_DURATION + NIGHTTIME_DURATION
i = 0
while day_duration * i < collect_steps * collect_interval:
    plt.axvspan((i * day_duration + DAYTIME_DURATION) / collect_interval, (i+1)
                * day_duration / collect_interval, color="midnightblue", alpha=0.4)
    i += 1

plt.xlim((0, collect_steps-1))

# Generate plot
x = np.arange(collect_steps)
plt.fill_between(x, np.min(collected_data, axis=0), np.max(
    collected_data, axis=0), alpha=.5, linewidth=0)
plt.plot(x, np.median(collected_data, axis=0), linewidth=2)

# Clean up & save plot
plt.title(
    f"Tuna distribution among {runs} simulations of {collect_steps * collect_interval} steps.")
plt.xlabel("Time")
plt.ylabel("Average neighbour count")
plt.savefig(f"daylight-average-neighbourcount.svg",
            transparent=True, format="svg", bbox_inches="tight")
