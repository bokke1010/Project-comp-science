# Simulation options
TIME_STEPS = 120

GRID_X = 120
GRID_Y = 120

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
FISH_START_RADIUS = 2
FISH_START_COUNT = 5
FISH_START_CHANCE = 0.7

FOOD_START_COUNT = 10

SHARK_START_COUNT = 7

# Fish settings
FISH_SPEED = 1
FISH_VISION = 2
FISH_RANDOMNESS = 0.3

# Fish influence factors
SHARK_FACTOR = 5
FOOD_ATTRACTION = 3

# Shark settings
SHARK_SPEED = 0.8
SHARK_VISION = 4


