import main
import numpy as np
from matplotlib import pyplot as plt
from parameters import *

main.SIZE_X = GRID_X
main.SIZE_Y = GRID_Y

collect_steps = 120
collect_interval = 1
collect_range = 2
ncount = len(list(main.get_neighbourhood(0,0,collect_range))) + 1
neighbourdata = np.empty(shape=(collect_steps, ncount), dtype=int)

runs = 10
collected_data = np.zeros(shape=(runs, ncount), dtype=int)

sim = main.Simulation( # Use default parameters
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

for i in range(runs):
    neighbourdata.fill(0)
    sim.simulate(collect_steps * collect_interval, [main.collect_data(collect_range, neighbourdata)], [collect_interval], FOOD_START_COUNT, [FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE], [], SHARK_START_COUNT)
    collected_data[i] = np.sum(neighbourdata, axis=0)

plt.bar(
    np.arange(collected_data.shape[1]),
    np.mean(collected_data, axis=0),
    yerr=np.array([np.min(collected_data, axis=0), np.max(collected_data, axis=0)]),
    capsize=5,
    tick_label=list(map(str, np.arange(collected_data.shape[1]))))
plt.show()
