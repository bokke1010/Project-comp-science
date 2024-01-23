from parameters import *
from dataclasses import dataclass
from random import randrange, random, choice
from math import sin, cos, atan2, pi, floor, ceil
import numpy as np
import visualize
from PerlinNoise import generate_perlin_noise 


CELL_EMPTY = 1
CELL_FISH = 2
CELL_SHARK = 3
CELL_FOOD = 4
CELL_OBSTACLE = 5

FISH_REPLACEABLE = [CELL_EMPTY, CELL_FOOD]
SHARK_REPLACEABLE = [CELL_EMPTY, CELL_FOOD, CELL_FISH]

#REMEMBER: 0,0 is top left
DIR_COUNT = 6

# Direction symbols in order of ascending angle, including marker
dir_symbs = ['→', '↘', '↙', '←', '↖', '↗']

dir_to_angle = [0, pi / 3, 2 * pi / 3, pi, 4 * pi / 3, 5 * pi / 3]

def angle_to_dir(angle):
    """Simple conversion from angle in radians to one of 6 directions."""
    part = 2 * pi / DIR_COUNT
    result = int(floor((angle + part/2) / part)) % DIR_COUNT
    # print(angle / pi, result)
    return result

def offset_to_dir(x, y):
    """Turn a nonzero vector into a direction, not grid coordinates"""
    return angle_to_dir(atan2(y, x))

def print_hline(len, up = True, down = True):
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
    return np.array([cos(angle), sin(angle)])

def dir_to_pos(x, y, dir, dist):
    if GRID_MODE == MODE_4:
        pass
    elif GRID_MODE == MODE_6:
        assert 0 <= dir < 6
        m = y & 1
        nx = 0
        if dir % 3 == 0: # East, West
            nx = dist * (1-2 * (dir // 3))
        elif dir & 1 == 0: # Northwest, southwest
            nx = - (dist - m) // 2
        else: # Northeast, southeast
            nx = (dist + m) // 2

        ny = dist * int(dir % 3 != 0) * (1 - 2 * (dir // 3))
        return np.array([x + nx, y + ny])
    elif GRID_MODE == MODE_8:
        pass

def get_neighbourhood(mx, my, r = 1, include_self = False):
    if GRID_MODE == MODE_4:
        for x in range(-r, r+1):
            for y in range(-r + abs(x), r + 1 - abs(x)):
                if x == 0 and y == 0 and not include_self:
                    continue
                yield np.array([mx + x, my + y])
    elif GRID_MODE == MODE_6:
        # Odd rows are shifted 1/2 to the right
        # m is 1 if we are on an odd row
        m = my & 1
        for y in range(-r, r+1):
            # X range goes from r+1 elements to 2r+1 elements
            for x in range(-r + ((abs(y) + m) // 2), r + 1 - ((abs(y) + 1 - m) // 2)):
                if x == 0 and y == 0 and not include_self:
                    continue
                yield np.array([mx + x, my + y])


    elif GRID_MODE == MODE_8:
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                if x == 0 and y == 0 and not include_self:
                    continue
                yield np.array([mx + x, my + y])

def pos_to_dir(source_x, source_y, target_x, target_y):
    dx = target_x - source_x
    dy = target_y - source_y

    if GRID_MODE == MODE_4:
        return offset_to_dir(dx, dy)
    elif GRID_MODE == MODE_6:
        m_source = source_y & 1
        m_target = target_y & 1

        dx -= (dy - m_target) // 2 - (dy - m_source) // 2
        return offset_to_dir(dx, dy)
    elif GRID_MODE == MODE_8:
        pass 

def calculate_distance(x1, y1, x2, y2):
        m1 = y1 & 1
        m2 = y2 & 1

        x1 -= (y1 - m1) // 2
        x2 -= (y2 - m2) // 2

        return max(abs(x2 - x1), abs(y2 - y1), abs(x1 + y1 - x2 - y2))


@dataclass
class Grid_cell:
    cell_type: int = 1 # CELL_EMPTY
    cell_dir: int = 0 # Unused by most cell types
    food_lifespan: int = 0

    def __repr__(self):
        if self.cell_type == CELL_EMPTY:
            return " "
        elif self.cell_type == CELL_SHARK:
            return "S"
        elif self.cell_type == CELL_FOOD:
            return "F"
        else:
            return dir_symbs[self.cell_dir]


class Grid():

    # grid : [[Grid_cell]]

    def __init__(self):
        self.grid  = [[Grid_cell()] * GRID_X for _ in range(GRID_Y)]

    def __repr__(self):
        return '│' + "│\n│".join((' ' * (i & 1)) + " ".join(map(repr, line)) + (' ' * (1 - (i & 1))) for (i, line) in enumerate(self.grid)) + '│'

    def set_position(self, x, y, value):
        self.grid[y%GRID_Y][x%GRID_X] = value
        # Can be made more efficient by limiting to [-l, l] and letting python handle it

    def get_position(self, x,y) -> Grid_cell:
        return self.grid[y%GRID_Y][x%GRID_X]
        
    def cmp_position(self, x, y, type):
        return self.get_position(x, y).cell_type == type

    def populate_fish(self, count, radius, chance):
        for i in range(count):
            cluster_x, cluster_y = randrange(0, GRID_X), randrange(0, GRID_Y)
            cluster_dir = randrange(0,DIR_COUNT) # None is no option
            for (x, y) in get_neighbourhood(cluster_x, cluster_y, radius, True):
                if random() < chance:
                    if self.get_position(x,y).cell_type not in FISH_REPLACEABLE:
                        continue
                    fish_cell = Grid_cell()
                    fish_cell.cell_type = CELL_FISH
                    fish_cell.cell_dir = cluster_dir
                    self.set_position(x,y, fish_cell)

    def populate_sharks(self, count):
        for i in range(count):
            x, y = randrange(0, GRID_X), randrange(0, GRID_Y)
            shark_cell = Grid_cell()
            shark_cell.cell_type = CELL_SHARK
            self.set_position(x, y, shark_cell)

    def place_food(self, count):
        for i in range(count):
            x, y = randrange(0, GRID_X), randrange(0, GRID_Y)
            if self.get_position(x,y).cell_type != CELL_EMPTY:
                continue
            food_cell = Grid_cell()
            food_cell.cell_type = CELL_FOOD
            self.set_position(x, y, food_cell)

    # def regenerate_food(self):
    #     for y in range(GRID_Y):
    #         for x in range(GRID_X):
    #             cell = self.grid[y][x]
    #             if cell.cell_type == CELL_FOOD and cell.food_lifespan > 0:
    #                 cell.food_lifespan -= 1
    #                 if cell.food_lifespan == 0:
    #                     # Food has reached the end of its lifespan, replace with an empty cell
    #                     self.set_position(x, y, Grid_cell())
            
    def place_obstacles(self, density_obstacle, threshold_obstacle):

        width = len(self.grid[0])
        height = len(self.grid)

        scale = 25 # lower scale is zoomed out
        mask_scale = 60
        line_thickness = 0.01 # lower is thinner lines
        line_count = 3 # amount of lines
        
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
        for y in range(0, GRID_Y):
            for x in range(0, GRID_X):
                self.grid[y][x] = Grid_cell()

def move_fish(old_grid, new_grid, is_daytime): # finialize timestep
    for y in range(GRID_Y):
        for x in range(GRID_X):
            new_local_cell = new_grid.get_position(x,y)
            old_local_cell = old_grid.get_position(x,y)

            if old_local_cell.cell_type == CELL_FISH:

                sx, sy = 0, 0 # field coordinates, not grid coordinates
                rvec = FISH_RANDOMNESS * unit_vector(random() * 2 * pi)
                sx += rvec[0]
                sy += rvec[1]
                for (nx, ny) in get_neighbourhood(x, y, FISH_VISION + is_daytime * DAYTIME_VISION_BONUS, True):
                    other_pos = old_grid.get_position(nx, ny)
                    # Assert fish present
                    if other_pos.cell_type == CELL_FISH:
                        other_dir = unit_vector(dir_to_angle[other_pos.cell_dir])
                        sx += other_dir[0]
                        sy += other_dir[1]
                        if USE_COHESION and calculate_distance(x, y, nx, ny) > 1:
                            cohesion_vector = unit_vector(dir_to_angle[pos_to_dir(x, y, nx, ny)])
                            sx += COHESION_STRENGTH * cohesion_vector[0]
                            sy += COHESION_STRENGTH * cohesion_vector[1]
                    # If shark present, influence to other direction
                    elif other_pos.cell_type == CELL_SHARK:
                        escape_vector = unit_vector(dir_to_angle[pos_to_dir(nx, ny, x, y)])
                        sx += SHARK_FACTOR * escape_vector[0]
                        sy += SHARK_FACTOR * escape_vector[1]
                    elif other_pos.cell_type == CELL_FOOD:
                        food_vector = unit_vector(dir_to_angle[pos_to_dir(x, y, nx, ny)])
                        sx += FOOD_ATTRACTION * food_vector[0]
                        sy += FOOD_ATTRACTION * food_vector[1]
                    elif other_pos.cell_type == CELL_OBSTACLE:
                        escape_vector = unit_vector(dir_to_angle[pos_to_dir(nx, ny, x, y)])
                        sx += OBSTACLE_FACTOR * escape_vector[0]
                        sy += OBSTACLE_FACTOR * escape_vector[1]
                    else:
                        continue
                dir = old_local_cell.cell_dir
                if sx != 0 or sy != 0:
                    dir = offset_to_dir(sx, sy)
                    old_local_cell.cell_dir = dir
                (nx, ny) = dir_to_pos(x, y, dir, 1)

                if (new_grid.get_position(nx, ny).cell_type in FISH_REPLACEABLE) \
                    and (old_grid.get_position(nx, ny).cell_type in FISH_REPLACEABLE):
                    new_grid.set_position(nx, ny, old_local_cell)
                elif (new_local_cell.cell_type in FISH_REPLACEABLE):
                    new_grid.set_position(x, y, old_local_cell)

            elif old_local_cell.cell_type == CELL_SHARK:
                if random() > SHARK_SPEED:
                    new_grid.set_position(x, y, old_local_cell)
                    continue

                valid_neighbors = [(nx, ny) for nx, ny in get_neighbourhood(x, y) if
                                    new_grid.get_position(nx, ny).cell_type in SHARK_REPLACEABLE and
                                    old_grid.get_position(nx, ny).cell_type in SHARK_REPLACEABLE]
                
                if not valid_neighbors:
                    new_grid.set_position(x, y, old_local_cell)
                    continue

                # Check if any fish are in vision
                if all(not old_grid.cmp_position(nx, ny, CELL_FISH) for nx, ny in get_neighbourhood(x, y, SHARK_VISION)):
                    # Move to a random neighbor cell
                    nx, ny = choice(valid_neighbors)
                    new_grid.set_position(nx, ny, old_local_cell)
                else:
                    # Choose a target
                    targets = [(nx, ny) for nx, ny in get_neighbourhood(x, y, SHARK_VISION) if old_grid.cmp_position(nx, ny, CELL_FISH)]
                    
                    # Go to closest valid target
                    (nx, ny) = min(targets, key=lambda coords : calculate_distance(x, y, *coords))
                    (tx, ty) = min(valid_neighbors, key=lambda coords : calculate_distance(nx, ny, *coords))
                    new_grid.set_position(tx, ty, old_local_cell)


            elif old_local_cell.cell_type == CELL_FOOD and new_local_cell.cell_type == CELL_EMPTY:
                new_grid.set_position(x,y, old_local_cell)
            elif old_local_cell.cell_type == CELL_OBSTACLE:
                new_grid.set_position(x,y,old_local_cell)



def iterate_grid(grid, steps):
    new_grid = Grid()
    daytime = 1
    time = 0
    for i in range(steps):
        if i % 10 == 0:
            visualize.visualize(new_grid)
        new_grid.clear()
        new_grid.place_food(1)
        if random() < FISH_RANDOMNESS:
            new_grid.populate_fish(1,0,1)
        move_fish(grid, new_grid, daytime)

        time += 1
        if (daytime and time > DAYTIME_DURATION) or (not daytime and time > NIGHTTIME_DURATION):
            time = 0
            daytime = 1 - daytime
        grid, new_grid = new_grid, grid
    return grid

if __name__ == "__main__":
    grid = Grid()

    grid.place_obstacles(DENSITY_OBSTACLE, THRESHOLD_OBSTACLE)

    grid.place_food(FOOD_START_COUNT)
    grid.populate_fish(FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE)
    grid.populate_sharks(SHARK_START_COUNT)
    visualize.init(GRID_X, GRID_Y, GRID_MODE)
    grid = iterate_grid(grid, TIME_STEPS)
    visualize.finish()
