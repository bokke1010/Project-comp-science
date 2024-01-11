from parameters import *
from dataclasses import dataclass
from random import randrange, random


CELL = {
    "EMPTY" : 1,
    "FISH"  : 2,
    "SHARK" : 3
}

#REMEMBER: 0,0 is top left
DIRS = {
    "N"     : 0,
    "NE"    : 1,
    "E"     : 2,
    "SE"    : 3,
    "S"     : 4,
    "SW"    : 5,
    "W"     : 6,
    "NW"    : 7,
    "NONE"  : 8,
    "MARKED": 9
}

# Direction symbols, including marker
dir_symbs = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖', 'o', 'X']

dir_to_offset = [(0,-1),(1,-1), (1,0), (1,1), (0,1), (-1, 1), (-1, 0), (-1, -1), (0,0)]

offset_to_dir = {
    (0,-1)  : 0,
    (1,-1)  : 1,
    (1,0)   : 2,
    (1,1)   : 3,
    (0,1)   : 4,
    (-1, 1) : 5,
    (-1, 0) : 6,
    (-1, -1): 7,
    (0,0)   : 8
}

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


@dataclass
class Grid_cell:
    cell_type: int = CELL["EMPTY"]
    cell_dir: int = DIRS["NONE"]

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
        return '│' + "│\n│".join(" ".join(map(repr, line)) for line in self.grid) + '│'

    def set_position(self, x, y, value):
        self.grid[y%GRID_Y][x%GRID_X] = value

    def get_position(self, x,y) -> Grid_cell:
        return self.grid[y%GRID_Y][x%GRID_X]

    def populate_fish(self, count, radius, chance):
        for i in range(count):
            cluster_x, cluster_y = randrange(0, GRID_X), randrange(0, GRID_Y)
            for x in range(cluster_x-radius, cluster_x+radius+1):
                for y in range(cluster_y-radius, cluster_y+radius+1):
                    if random() < chance:
                        fish_cell = Grid_cell()
                        fish_cell.cell_type = CELL["FISH"]
                        fish_cell.cell_dir = randrange(0,8)
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

def sgn(n):
    return int(n > 0) - int(n < 0)

def assign_direction(old_grid, new_grid, x, y): # single fish alignment
    sx, sy = 0, 0
    for (dx, dy) in dir_to_offset[0:8]:
        other_pos = old_grid.get_position(x + dx, y + dy)
        if other_pos.cell_type == CELL["EMPTY"]:
            continue
        other_dir = other_pos.cell_dir
        sx += dir_to_offset[other_dir][0]
        sy += dir_to_offset[other_dir][1]
    if sx != 0 or sy != 0:
        new_fish = Grid_cell()
        new_fish.cell_type = CELL['FISH']
        new_fish.cell_dir = offset_to_dir[(sgn(sx), sgn(sy))]
        new_grid.set_position(x,y, new_fish)
    else:
        new_grid.set_position(x,y, old_grid.get_position(x, y))



def assign_directions(old_grid, new_grid): # alignment rule
    for y in range(GRID_Y):
        for x in range(GRID_X):
            if old_grid.get_position(x,y).cell_type == CELL["FISH"]:
                assign_direction(old_grid, new_grid, x,y)

def move_fish(old_grid, new_grid): # finialize timestep
    for y in range(GRID_Y):
        for x in range(GRID_X):
            n_cell = new_grid.get_position(x,y)
            o_cell = old_grid.get_position(x,y)
            if o_cell.cell_type != CELL["FISH"]:
                continue
            offset = dir_to_offset[n_cell.cell_dir]
            nx, ny = x + offset[0], y + offset[1]
            m_cell = new_grid.get_position(nx, ny)
            if m_cell.cell_type != CELL["EMPTY"]:
                continue
            new_grid.set_position(x,y, Grid_cell())
            new_grid.set_position(nx, ny, n_cell)


def iterate_grid(grid, steps):
    new_grid = Grid()
    print_hline(GRID_X * 2 + 1, False, True)
    for i in range(steps):
        new_grid.clear()
        assign_directions(grid, new_grid)
        move_fish(grid, new_grid)
        print(new_grid)
        print_hline(GRID_X * 2 + 1, True, i != steps - 1)
        grid, new_grid = new_grid, grid
    return grid



grid = Grid()

grid.populate_fish(FISH_START_COUNT, FISH_START_RADIUS, FISH_START_CHANCE)
grid = iterate_grid(grid, 8)
