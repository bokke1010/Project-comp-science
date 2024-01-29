import main
from math import pi
import numpy as np

# Recall dir_symbs to convert direction indices to 2D directions
print(main.dir_symbs)

# Test angle_to_dir in a simple case
assert (main.angle_to_dir(main.dir_to_angle[2]) == 2)

# Test inbetween case (should round up)
assert (main.angle_to_dir(pi / 2) == 2)

# Test a number of distance checks
assert (main.calculate_distance(0, 0, 3, 0) == 3)
assert (main.calculate_distance(0, 0, 1, 2) == 2)
assert (main.calculate_distance(0, 0, -1, 2) == 2)
assert (main.calculate_distance(0, 0, 2, 1) == 3)

# Test dir_to_pos on a non-horizontal angle
assert (main.dir_to_pos(2, 2, 4, 2)[0] == 1)
assert (main.dir_to_pos(2, 2, 4, 2)[1] == 0)

# Test get_neighbourhood
assert ((0, 1) in list(map(tuple, main.get_neighbourhood(2, 2, 2, False))))
assert ((4, 1) not in list(map(tuple, main.get_neighbourhood(2, 2, 2, False))))
assert (len(list(main.get_neighbourhood(3, -5, 1, False))) == 6)
assert (len(list(main.get_neighbourhood(2, 2, 3, False))) == 36)

# Test offset and pos to dir
assert (main.offset_to_dir(0, 2) == 2)
assert (main.pos_to_dir(1, 1, 2, 4) == 1)
