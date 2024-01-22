# Simulation options
TIME_STEPS = 600

GRID_X = 150
GRID_Y = 150

#Visualization options
class VisualizationOptions:
    FPS = 5
    CELLS_PER_INCH = 5
    PIXELS_PER_CELL = 5
    PIXELS_PER_ENTITY = 6 # May be larger than pixels per cell
    PIXELS_PER_INCH = CELLS_PER_INCH * PIXELS_PER_CELL
    FILE_NAME = "video"
    BG_COLOR = "darkblue"

# Only mode 6 is supported
MODE_4, MODE_6, MODE_8 = 0,1,2
GRID_MODE = MODE_6

# Initialization settings
FISH_START_RADIUS = 8
FISH_START_COUNT = 2
FISH_START_CHANCE = 0.3
FISH_REINFORCEMENT_CHANCE = 0.5

FOOD_START_COUNT = 10

SHARK_START_COUNT = 12

# Fish settings
FISH_SPEED = 1
FISH_VISION = 2
FISH_RANDOMNESS = 0.3

# Fish influence factors
SHARK_FACTOR = 5
FOOD_ATTRACTION = 3
OBSTACLE_FACTOR = 1.2

# Shark settings
SHARK_SPEED = 0.8
SHARK_VISION = 4

# Obstacle settings 

DENSITY_OBSTACLE = 0.3
THRESHOLD_OBSTACLE = 0.3

# Time settings
DAYTIME_DURATION = 50
NIGHTTIME_DURATION = 30
DAYTIME_VISION_BONUS = 1
