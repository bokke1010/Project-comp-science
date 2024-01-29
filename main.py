# main.py
# This file contains all grid and simulation code.
# It can be imported by other files to collect data or
# create visualizations.

from dataclasses import dataclass
from random import randrange, random, choice
from math import sin, cos, atan2, pi, floor, ceil
import numpy as np
from PerlinNoise import generate_perlin_noise

# Define cell type indices
CELL_EMPTY = 1
CELL_FISH = 2
CELL_SHARK = 3
CELL_FOOD = 4
CELL_OBSTACLE = 5

# Define what cells may eat what other cells
FISH_REPLACEABLE = [CELL_EMPTY, CELL_FOOD]
SHARK_REPLACEABLE = [CELL_EMPTY, CELL_FOOD, CELL_FISH]


# REMEMBER: 0,0 is top left
SIZE_X, SIZE_Y = None, None

# Direction 0 is east, 3 is west
# Using typical radian ordering but with positive y going in the downwards direction
# See symbol indices for clarification
DIR_COUNT = 6
dir_symbs = ['→', '↘', '↙', '←', '↖', '↗']

# Simple map [dir -> dir * pi / 3] to map direction indices to angles
dir_to_angle = [0, pi / 3, 2 * pi / 3, pi, 4 * pi / 3, 5 * pi / 3]


def angle_to_dir(angle):
    """Simple conversion from angle in radians to one of 6 directions.

    Opposite of dir_to_angle, but as a function.
    """
    part = 2 * pi / DIR_COUNT
    result = int(floor((angle + part/2) / part)) % DIR_COUNT
    # print(angle / pi, result)
    return result


def offset_to_dir(x, y):
    """Turn a nonzero vector into a direction.

    This function uses a offset in the 2D plane, not grid coordinates.
    """
    assert (x != 0 or y != 0)
    return angle_to_dir(atan2(y, x))


def pos_to_dir(source_x, source_y, target_x, target_y):
    """Turn a nonzero vector into a direction.

    This function uses grid coordinates, not an offset in the 2D plane.
    """
    dx = target_x - source_x
    dy = target_y - source_y
    m_source = source_y & 1
    m_target = target_y & 1

    dx -= (dy - m_target) // 2 - (dy - m_source) // 2
    return offset_to_dir(dx, dy)


def print_hline(len, up=True, down=True):
    """DEPRECATED

    Print a horizontal line of a given length, with the ends pointing up or down as required.
    """
    s, e = None, None
    if up and down:
        s, e = '├', '┤'
    elif up and not down:
        s, e = '└', '┘'
    elif down and not up:
        s, e = '┌', '┐'
    else:
        s, e = '╶', '╴'

    print(s + '─' * (len - 2) + e)


def unit_vector(angle):
    """Convert some angle in radians into a unit vector with that direction."""
    return np.array([cos(angle), sin(angle)])


def dir_to_pos(x, y, dir, dist):
    """Move [dist] steps into [dir] direction from [x], [y]"""
    assert 0 <= dir < 6
    m = y & 1
    nx = 0
    if dir % 3 == 0:  # East, West
        nx = dist * (1-2 * (dir // 3))
    elif dir & 1 == 0:  # Northwest, southwest
        nx = - (dist - m) // 2
    else:  # Northeast, southeast
        nx = (dist + m) // 2

    ny = dist * int(dir % 3 != 0) * (1 - 2 * (dir // 3))
    return np.array([x + nx, y + ny])


def get_neighbourhood(mx, my, r=1, include_self=False):
    """Get all cells within [r] distance from [mx], [my], possibly including ([mx,my])."""
    m = my & 1
    for y in range(-r, r+1):
        for x in range(-r + ((abs(y) + m) // 2), r + 1 - ((abs(y) + 1 - m) // 2)):
            if x == 0 and y == 0 and not include_self:
                continue
            yield np.array([mx + x, my + y])


def calculate_distance(x1, y1, x2, y2):
    """Calculate the distance between two grid coordinates."""
    m1 = y1 & 1
    m2 = y2 & 1

    x1 -= (y1 - m1) // 2
    x2 -= (y2 - m2) // 2

    return max(abs(x2 - x1), abs(y2 - y1), abs(x1 + y1 - x2 - y2))


@dataclass
class Grid_cell:
    cell_type: int = 1  # CELL_EMPTY
    cell_dir: int = 0  # Unused by most cell types

    def __repr__(self):
        """Print some symbol to represent the cell. Can be used to display the grid as text"""
        if self.cell_type == CELL_EMPTY:
            return " "
        elif self.cell_type == CELL_SHARK:
            return "S"
        elif self.cell_type == CELL_FOOD:
            return "O"
        elif self.cell_type == CELL_OBSTACLE:
            return "X"
        else:
            return dir_symbs[self.cell_dir]


class Grid():
    """A class to represent a singular grid in a cellular automata.

    This grid contains hexagonal cells and uses the globals SIZE_X, SIZE_Y to initialize the size.\n
    Using set_position, cmp_position and get_position takes any wraparound into account, so 0 <= x < SIZE_X (likewise for y) is not required.\n
    The class also contains some functions to generate the different types of grid cells, including default generation settings.
    """

    def __init__(self):
        self.grid = [[Grid_cell()] * SIZE_X for _ in range(SIZE_Y)]

    def __repr__(self):
        """DEPRECATED\nPrint the grid as text"""
        return '│' + "│\n│".join((' ' * (i & 1)) + " ".join(map(repr, line)) + (' ' * (1 - (i & 1))) for (i, line) in enumerate(self.grid)) + '│'

    def set_position(self, x, y, value):
        """Place a [value] at [x],[y].

        Includes wraparound.
        """
        self.grid[y % SIZE_Y][x % SIZE_X] = value

    def get_position(self, x, y) -> Grid_cell:
        """Get the grid cell at [x],[y].

        Includes wraparound.
        """
        return self.grid[y % SIZE_Y][x % SIZE_X]

    def cmp_position(self, x, y, type):
        """Compare the grid cell type at [x],[y] with [type].

        Includes wraparound.
        """
        return self.get_position(x, y).cell_type == type

    def populate_fish(self, count=2, radius=8, chance=0.3):
        """Place [count] clusters of fish in the grid, with a chance [chance] for each cell in radius [radius] (0 for single fish) to exist. Skips invalid locations."""
        for i in range(count):
            cluster_x, cluster_y = randrange(0, SIZE_X), randrange(0, SIZE_Y)
            cluster_dir = randrange(0, DIR_COUNT)  # None is no option
            for (x, y) in get_neighbourhood(cluster_x, cluster_y, radius, True):
                if random() < chance:
                    if self.get_position(x, y).cell_type not in FISH_REPLACEABLE:
                        continue
                    fish_cell = Grid_cell()
                    fish_cell.cell_type = CELL_FISH
                    fish_cell.cell_dir = cluster_dir
                    self.set_position(x, y, fish_cell)

    def populate_sharks(self, count):
        """Place [count] sharks randomly in the grid."""
        for i in range(count):
            x, y = randrange(0, SIZE_X), randrange(0, SIZE_Y)
            shark_cell = Grid_cell()
            shark_cell.cell_type = CELL_SHARK
            self.set_position(x, y, shark_cell)

    def place_food(self, count):
        """Place [count] food randomly in the grid. Skips invalid locations."""
        for i in range(count):
            x, y = randrange(0, SIZE_X), randrange(0, SIZE_Y)
            if self.get_position(x, y).cell_type != CELL_EMPTY:
                continue
            food_cell = Grid_cell()
            food_cell.cell_type = CELL_FOOD
            self.set_position(x, y, food_cell)

    def place_obstacles(self,
                        scale=25,  # scale of obstacle walls (lower is larger)
                        mask_scale=60,  # scale of larger structures
                        line_thickness=0.01,  # lower is thinner lines
                        line_count=3,  # amount of lines in the gradient
                        density_obstacle=0.3
                        ):
        """Generates obstacles with a pair of perlin noise maps.

        The main obstacle map has scale [scale] and generates rocks if the
        value of that map at those coordinates falls in one of [line_count]
        evenly spaced intervals of length 2 * [line_thickness].

        Then the second map with scale [mask_scale] only allows obstacles to
        exist if it is above [density_obstacle] at that position.
        """
        width = len(self.grid[0])
        height = len(self.grid)

        values = [(i + 1) / (line_count + 1) for i in range(line_count)]
        perlin_noise_map = generate_perlin_noise(width, height, scale)

        mask_noise_map = generate_perlin_noise(width, height, mask_scale)

        for y in range(height):
            for x in range(width):

                if any(v - line_thickness < perlin_noise_map[y, x] < v + line_thickness for v in values) and mask_noise_map[y, x] < density_obstacle:
                    obstacle_cell = Grid_cell()
                    obstacle_cell.cell_type = CELL_OBSTACLE
                    self.set_position(x, y, obstacle_cell)

    def clear(self):
        """Replace all cells with empty cells."""
        for y in range(0, SIZE_Y):
            for x in range(0, SIZE_X):
                self.grid[y][x] = Grid_cell()


class Simulation:
    def __init__(self, fish_vision, shark_vision, fish_randomness,
                 cohesion_strength, shark_factor, food_attraction, obstacle_factor,
                 shark_speed, food_per_step, fish_reinforcement_chance,
                 daytime_duration, nighttime_duration, daytime_bonus):
        """Create a simulation environment with all available parameters."""
        self.fish_vision = fish_vision
        self.shark_vision = shark_vision
        self.fish_randomness = fish_randomness
        self.cohesion_strength = cohesion_strength
        self.shark_factor = shark_factor
        self.food_attraction = food_attraction
        self.obstacle_factor = obstacle_factor
        self.shark_speed = shark_speed
        self.food_per_step = food_per_step
        self.fish_reinforcement_chance = fish_reinforcement_chance
        self.daytime_duration = daytime_duration
        self.nighttime_duration = nighttime_duration
        self.daytime_bonus = daytime_bonus

    def move_fish(self, old_grid, new_grid, daytime):
        """ Compute a new grid that is the result of a single timestap simulation."""
        for y in range(SIZE_Y):
            for x in range(SIZE_X):
                new_local_cell = new_grid.get_position(x, y)
                old_local_cell = old_grid.get_position(x, y)

                # Simulate fish movement
                if old_local_cell.cell_type == CELL_FISH:

                    sx, sy = 0, 0  # field coordinates, not grid coordinates
                    rvec = self.fish_randomness * \
                        unit_vector(random() * 2 * pi)
                    sx += rvec[0]
                    sy += rvec[1]

                    # add up all neighbour factors
                    for (nx, ny) in get_neighbourhood(x, y,
                                                      self.fish_vision + (daytime * self.daytime_bonus), True):
                        other_pos = old_grid.get_position(nx, ny)

                        if other_pos.cell_type == CELL_FISH:
                            other_dir = unit_vector(
                                dir_to_angle[other_pos.cell_dir])
                            sx += other_dir[0]
                            sy += other_dir[1]
                            if self.cohesion_strength > 0 and \
                                    calculate_distance(x, y, nx, ny) > 1:
                                cohesion_vector = unit_vector(
                                    dir_to_angle[pos_to_dir(x, y, nx, ny)])
                                sx += self.cohesion_strength * \
                                    cohesion_vector[0]
                                sy += self.cohesion_strength * \
                                    cohesion_vector[1]
                        # If shark present, influence to other direction
                        elif other_pos.cell_type == CELL_SHARK:
                            escape_vector = unit_vector(
                                dir_to_angle[pos_to_dir(nx, ny, x, y)])
                            sx += self.shark_factor * escape_vector[0]
                            sy += self.shark_factor * escape_vector[1]
                        elif other_pos.cell_type == CELL_FOOD:
                            food_vector = unit_vector(
                                dir_to_angle[pos_to_dir(x, y, nx, ny)])
                            sx += self.food_attraction * food_vector[0]
                            sy += self.food_attraction * food_vector[1]
                        elif other_pos.cell_type == CELL_OBSTACLE:
                            escape_vector = unit_vector(
                                dir_to_angle[pos_to_dir(nx, ny, x, y)])
                            sx += self.obstacle_factor * escape_vector[0]
                            sy += self.obstacle_factor * escape_vector[1]
                        else:
                            continue

                    # Average out all influences into a single direction
                    dir = old_local_cell.cell_dir
                    if sx != 0 or sy != 0:
                        dir = offset_to_dir(sx, sy)
                        old_local_cell.cell_dir = dir
                    (nx, ny) = dir_to_pos(x, y, dir, 1)

                    # Move if that direction is valid
                    if (new_grid.get_position(nx, ny).cell_type in FISH_REPLACEABLE) \
                            and (old_grid.get_position(nx, ny).cell_type in FISH_REPLACEABLE):
                        new_grid.set_position(nx, ny, old_local_cell)
                    elif (new_local_cell.cell_type in FISH_REPLACEABLE):
                        new_grid.set_position(x, y, old_local_cell)

                # Simulate shark movement
                elif old_local_cell.cell_type == CELL_SHARK:
                    # Sharks don't always move
                    if random() > self.shark_speed:
                        new_grid.set_position(x, y, old_local_cell)
                        continue

                    # Filter available positions
                    valid_neighbors = [(nx, ny) for nx, ny in get_neighbourhood(x, y) if
                                       new_grid.get_position(nx, ny).cell_type in SHARK_REPLACEABLE and
                                       old_grid.get_position(nx, ny).cell_type in SHARK_REPLACEABLE]

                    if not valid_neighbors:
                        new_grid.set_position(x, y, old_local_cell)
                        continue

                    # Check if any fish are in vision
                    if all(not old_grid.cmp_position(nx, ny, CELL_FISH) for nx, ny in get_neighbourhood(x, y, self.shark_vision)):
                        # Move to a random neighbor cell
                        nx, ny = choice(valid_neighbors)
                        new_grid.set_position(nx, ny, old_local_cell)
                    else:
                        # Choose a target
                        targets = [(nx, ny) for nx, ny in get_neighbourhood(
                            x, y, self.shark_vision) if old_grid.cmp_position(nx, ny, CELL_FISH)]

                        # Go to closest valid target
                        (nx, ny) = min(
                            targets, key=lambda coords: calculate_distance(x, y, *coords))
                        (tx, ty) = min(valid_neighbors,
                                       key=lambda coords: calculate_distance(nx, ny, *coords))
                        new_grid.set_position(tx, ty, old_local_cell)

                # Move rocks and obstacles to new grid
                elif old_local_cell.cell_type == CELL_FOOD and new_local_cell.cell_type == CELL_EMPTY:
                    new_grid.set_position(x, y, old_local_cell)
                elif old_local_cell.cell_type == CELL_OBSTACLE:
                    new_grid.set_position(x, y, old_local_cell)

    def iterate_grid(self, grid, steps, actions=[], intervals=[]):
        """ Iterate a preconfigured grid.

        You can pass functions to be executed periodically, parameters for functions passed into actions is (grid, i)
        """
        new_grid = Grid()
        daytime = 1
        time = 0
        food_remainder = 0
        for i in range(steps):
            # Run any additional tasks
            for action, interval in zip(actions, intervals):
                if action and i % interval == 0:
                    action(grid, i)

            # Add food and fish
            food_remainder += self.food_per_step
            new_grid.place_food(floor(food_remainder))
            food_remainder -= floor(food_remainder)

            if random() < self.fish_reinforcement_chance:
                new_grid.populate_fish(1, 0, 1)

            # Update simulation
            self.move_fish(grid, new_grid, daytime)

            # Manage day/night
            time += 1
            if (daytime and time > self.daytime_duration) or (not daytime and time > self.nighttime_duration):
                time = 0
                daytime = 1 - daytime

            # Prepare grid for next time step
            grid, new_grid = new_grid, grid
            new_grid.clear()
        return grid

    def simulate(self, steps, actions=None, intervals=1, food_start_count=0, fish_params=[], obstacle_params=[], shark_count=12):
        """ Run a simulation.

        Initial fish school parameters: \n
        count = 2, radius = 8, chance = 0.3 \n
        Obstacle generation parameters: \n
        scale = 25, mask_scale = 60, line_thickness = 0.01, line_count = 3, density_obstacle = 0.3
        """
        grid = Grid()

        grid.place_food(food_start_count)
        grid.place_obstacles(*obstacle_params)
        grid.populate_fish(*fish_params)
        grid.populate_sharks(shark_count)

        self.iterate_grid(grid, steps, actions, intervals)


def collect_data(collect_range, array):
    """Fills a numpy array such that a[t][n] contains the number of fish with n neighbours at sample t"""
    def inner_collect(g, t):
        for y in range(0, SIZE_Y):
            for x in range(0, SIZE_X):
                if g.grid[y][x].cell_type == CELL_FISH:
                    nc = 0
                    for (nx, ny) in get_neighbourhood(x, y, collect_range):
                        if g.cmp_position(nx, ny, CELL_FISH):
                            nc += 1
                    array[t][nc] += 1
    return inner_collect
