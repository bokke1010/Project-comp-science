from parameters import *
from dataclasses import dataclass
from random import randrange, random
from math import sin, cos, atan2, pi, floor, ceil
import numpy as np


CELL = {
    "EMPTY" : 1,
    "FISH"  : 2,
    "SHARK" : 3
}

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

@dataclass
class Grid_cell:
    cell_type: int = CELL["EMPTY"]
    cell_dir: int = 0 # Unused by default

    def __repr__(self):
        if self.cell_type == CELL["EMPTY"]:
            return " "
        elif self.cell_type == CELL["SHARK"]:
            return "S"
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

    def populate_fish(self, count, radius, chance):
        for i in range(count):
            cluster_x, cluster_y = randrange(0, GRID_X), randrange(0, GRID_Y)
            for (x, y) in get_neighbourhood(cluster_x, cluster_y, radius, True):
                if random() < chance:
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

    def clear(self):
        for y in range(0, GRID_Y):
            for x in range(0, GRID_X):
                self.grid[y][x] = Grid_cell()

# def sgn(n):
#     return int(n > 0) - int(n < 0)

def assign_direction(old_grid, new_grid, x, y): # single fish alignment
    sx, sy = 0, 0
    found = 0
    for (nx, ny) in get_neighbourhood(x, y, FISH_VISION, True):
        other_pos = old_grid.get_position(nx, ny)
        if other_pos.cell_type == CELL["EMPTY"]:
            continue
        found += 1
        other_dir = unit_vector(dir_to_angle[other_pos.cell_dir])
        sx += other_dir[0]
        sy += other_dir[1]
    if sx == 0 and sy == 0:
        new_grid.set_position(x,y, old_grid.get_position(x, y))
    else:
        new_fish = Grid_cell()
        new_fish.cell_type = CELL['FISH']
        new_fish.cell_dir = offset_to_dir(sx, sy)
        new_grid.set_position(x,y, new_fish)



def assign_directions(old_grid, new_grid): # alignment rule
    for y in range(GRID_Y):
        for x in range(GRID_X):
            if old_grid.get_position(x,y).cell_type == CELL["FISH"]:
                assign_direction(old_grid, new_grid, x,y)

def move_fish(old_grid, new_grid): # finialize timestep
    for y in range(GRID_Y):
        for x in range(GRID_X):
            new_local_cell = new_grid.get_position(x,y)
            old_local_cell = old_grid.get_position(x,y)
            if old_local_cell.cell_type != CELL["FISH"]:
                continue

            (nx, ny) = dir_to_pos(x, y, new_local_cell.cell_dir, 1)
            new_moved_cell = new_grid.get_position(nx, ny)
            old_moved_cell = old_grid.get_position(nx, ny)
            if new_moved_cell.cell_type != CELL["EMPTY"] or old_moved_cell.cell_type != CELL["EMPTY"]:
                continue
            new_grid.set_position(x,y, Grid_cell())
            new_grid.set_position(nx, ny, new_local_cell)


def iterate_grid(grid, steps):
    new_grid = Grid()
    print_hline(GRID_X * 2 + 2, False, True)
    print(grid)
    print_hline(GRID_X * 2 + 2, True, True)
    for i in range(steps):
        new_grid.clear()
        assign_directions(grid, new_grid)
        move_fish(grid, new_grid)
        print(new_grid)
        print_hline(GRID_X * 2 + 2, True, i != steps - 1)
        grid, new_grid = new_grid, grid
    return grid

if __name__ == "__main__":
    grid = Grid()

    grid.populate_fish(FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE)
    grid = iterate_grid(grid, 5)
