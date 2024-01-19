from parameters import *
from dataclasses import dataclass
from random import randrange, random, choice
from math import sin, cos, atan2, pi, floor, ceil
import numpy as np
import visualize


CELL = {
    "EMPTY" : 1,
    "FISH"  : 2,
    "SHARK" : 3,
    "FOOD"  : 4
}

FISH_REPLACEABLE = [CELL["EMPTY"], CELL["FOOD"]]
SHARK_REPLACEABLE = [CELL["EMPTY"], CELL["FOOD"], CELL["FISH"]]

#REMEMBER: 0,0 is top left
DIR_COUNT = 6

# Direction symbols in order of ascending angle, including marker
dir_symbs = ['→', '↘', '↙', '←', '↖', '↗']

dir_to_angle = [0, pi / 3, 2 * pi / 3, pi, 4 * pi / 3, 5 * pi / 3]

def angle_to_dir(angle):
    part = 2 * pi / DIR_COUNT
    result = int(floor((angle + part/2) / part)) % DIR_COUNT
    # print(angle / pi, result)
    return result

# Do not try to calculate the direction of a zero vector
def offset_to_dir(x, y):
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

        # ny = 1,2 is +1 | 0, 3 is 0 | 4, 5 is -1
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
    cell_type: int = CELL["EMPTY"]
    cell_dir: int = 0 # Unused by default
    food_lifespan: int = 0

    def __repr__(self):
        if self.cell_type == CELL["EMPTY"]:
            return " "
        elif self.cell_type == CELL["SHARK"]:
            return "S"
        elif self.cell_type == CELL["FOOD"]:
            return "F"
        else:
            return dir_symbs[self.cell_dir]
    # def __str__(self):
    #     return "member of Test"


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
            for (x, y) in get_neighbourhood(cluster_x, cluster_y, radius, True):
                if random() < chance:
                    if self.get_position(x,y).cell_type not in FISH_REPLACEABLE:
                        continue
                    fish_cell = Grid_cell()
                    fish_cell.cell_type = CELL["FISH"]
                    fish_cell.cell_dir = randrange(0,DIR_COUNT) # None is no optionn
                    self.set_position(x,y, fish_cell)

    def populate_sharks(self, count):
        for i in range(count):
            x, y = randrange(0, GRID_X), randrange(0, GRID_Y)
            shark_cell = Grid_cell()
            shark_cell.cell_type = CELL["SHARK"]
            # shark_cell.cell_dir = randrange(0, 9)
            self.set_position(x, y, shark_cell)

    def place_food(self, count):
        for i in range(count):
            x, y = randrange(0, GRID_X), randrange(0, GRID_Y)
            if self.get_position(x,y).cell_type != CELL["EMPTY"]:
                continue
            food_cell = Grid_cell()
            food_cell.cell_type = CELL["FOOD"]
            self.set_position(x, y, food_cell)

    # def place_food(self, count, lifespan):
    #     for i in range(count):
    #         x, y = randrange(0, GRID_X), randrange(0, GRID_Y)
    #         food_cell = Grid_cell()
    #         food_cell.cell_type = CELL["FOOD"]
    #         food_cell.food_lifespan = lifespan
    #         self.set_position(x, y, food_cell)

    # def regenerate_food(self):
    #     for y in range(GRID_Y):
    #         for x in range(GRID_X):
    #             cell = self.grid[y][x]
    #             if cell.cell_type == CELL["FOOD"] and cell.food_lifespan > 0:
    #                 cell.food_lifespan -= 1
    #                 if cell.food_lifespan == 0:
    #                     # Food has reached the end of its lifespan, replace with an empty cell
    #                     self.set_position(x, y, Grid_cell())



    def clear(self):
        for y in range(0, GRID_Y):
            for x in range(0, GRID_X):
                self.grid[y][x] = Grid_cell()

def move_fish(old_grid, new_grid): # finialize timestep
    for y in range(GRID_Y):
        for x in range(GRID_X):
            new_local_cell = new_grid.get_position(x,y)
            old_local_cell = old_grid.get_position(x,y)

            if old_local_cell.cell_type == CELL["FISH"]:

                sx, sy = 0, 0
                rvec = FISH_RANDOMNESS * unit_vector(random() * 2 * pi)
                sx += rvec[0]
                sy += rvec[1]
                for (nx, ny) in get_neighbourhood(x, y, FISH_VISION, True):
                    other_pos = old_grid.get_position(nx, ny)
                    # Assert fish present
                    if other_pos.cell_type == CELL["FISH"]:
                        other_dir = unit_vector(dir_to_angle[other_pos.cell_dir])
                        sx += other_dir[0]
                        sy += other_dir[1]
                    # If shark present, influence to other direction
                    elif other_pos.cell_type == CELL["SHARK"]:
                        sx += SHARK_FACTOR * (x - nx)
                        sy += SHARK_FACTOR * (y - ny)
                    elif other_pos.cell_type == CELL["FOOD"]:
                        sx += FOOD_ATTRACTION * (nx - x)
                        sy += FOOD_ATTRACTION * (ny - y)
                    else:
                        continue
                dir = old_local_cell.cell_dir
                if sx != 0 or sy != 0:
                    dir = offset_to_dir(sx, sy)
                    old_local_cell.cell_dir = dir
                (nx, ny) = dir_to_pos(x, y, offset_to_dir(sx, sy), 1)
                new_moved_cell = new_grid.get_position(nx, ny)
                old_moved_cell = old_grid.get_position(nx, ny)

                if (new_moved_cell.cell_type not in FISH_REPLACEABLE) or (old_moved_cell.cell_type not in FISH_REPLACEABLE):
                    new_grid.set_position(x, y, old_local_cell)
                    continue

                new_grid.set_position(nx, ny, old_local_cell)

            elif old_local_cell.cell_type == CELL["SHARK"]:
                if random() > SHARK_SPEED:
                    new_grid.set_position(x, y, old_local_cell)
                    continue

                valid_neighbors = [(nx, ny) for nx, ny in get_neighbourhood(x, y) if new_grid.get_position(nx, ny).cell_type in SHARK_REPLACEABLE]
                
                if not valid_neighbors:
                    new_grid.set_position(x, y, old_local_cell)
                    continue

                # Check if any fish are in vision
                if all(old_grid.get_position(nx, ny).cell_type != CELL["FISH"] for nx, ny in get_neighbourhood(x, y, SHARK_VISION)):
                    # Move to a random neighbor cell
                    nx, ny = choice(valid_neighbors)
                    new_grid.set_position(nx, ny, old_local_cell)
                else:
                    # Choose a target
                    targets = [(nx, ny) for nx, ny in get_neighbourhood(x, y, SHARK_VISION) if old_grid.get_position(nx, ny).cell_type == CELL["FISH"]]
                    
                    # Go to closest valid target
                    (nx, ny) = min(targets, key=lambda coords : calculate_distance(x, y, *coords))
                    (tx, ty) = min(valid_neighbors, key=lambda coords : calculate_distance(nx, ny, *coords))
                    new_grid.set_position(tx, ty, old_local_cell)


            elif old_local_cell.cell_type == CELL["FOOD"] and new_local_cell.cell_type == CELL["EMPTY"]:
                    new_grid.set_position(x,y, old_local_cell)



def iterate_grid(grid, steps):
    new_grid = Grid()
    # print_hline(GRID_X * 2 + 2, False, True)
    visualize.visualize(grid)
    # print(grid)
    # print_hline(GRID_X * 2 + 2, True, True)
    for i in range(steps):
        new_grid.clear()
        new_grid.place_food(1)
        new_grid.populate_fish(1,0,1)
        move_fish(grid, new_grid)
        visualize.visualize(new_grid)
        # print(new_grid)
        # print_hline(GRID_X * 2 + 2, True, i != steps - 1)
        grid, new_grid = new_grid, grid
    return grid

if __name__ == "__main__":
    grid = Grid()

    grid.place_food(FOOD_START_COUNT)
    grid.populate_fish(FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE)
    grid.populate_sharks(SHARK_START_COUNT)
    visualize.init(GRID_X, GRID_Y, GRID_MODE)
    grid = iterate_grid(grid, TIME_STEPS)
    visualize.finish()
