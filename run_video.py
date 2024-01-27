import main
import visualize
from parameters import *


grid = main.Grid()

grid.place_food(FOOD_START_COUNT)
grid.place_obstacles(DENSITY_OBSTACLE, THRESHOLD_OBSTACLE)

grid.populate_fish(FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE)
grid.populate_sharks(SHARK_START_COUNT)

visualize.init(GRID_X, GRID_Y)
# prep_data(TIME_STEPS, 2)

grid = main.iterate_grid(grid, TIME_STEPS, visualize.visualize, 1)

# for c in range(neighbourdata.shape[1] - 1):
#     neighbourdata[:,c+1] += neighbourdata[:,c]
#     plt.plot(neighbourdata[:,c], lw=0.5)
# plt.ylim((0, np.amax(neighbourdata) + 2))
# plt.show()

visualize.finish()
