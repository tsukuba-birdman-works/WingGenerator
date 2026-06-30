import numpy as np
from shapely.geometry import Polygon

# dummy stringer at x=-10
stringers = [Polygon([(-12, 10), (-8, 10), (-8, 8), (-12, 8)])]
miny, maxy = -5, 15
w = 2.0

def find_clear_x(start_x, w, miny, maxy, stringer_polys, direction):
    curr_x = start_x
    while True:
        leg_box = Polygon([
            (curr_x - w/2, miny - 20), (curr_x + w/2, miny - 20),
            (curr_x + w/2, maxy + 20), (curr_x - w/2, maxy + 20)
        ])
        min_dist = float('inf')
        for sp in stringer_polys:
            dist = leg_box.distance(sp)
            if dist < min_dist:
                min_dist = dist
        
        if not stringer_polys or min_dist >= 2.0:
            break
        curr_x += direction * 0.5
    return curr_x

start_x = -7.0
shifted = find_clear_x(start_x, w, miny, maxy, stringers, -1)
print(f"Shifted from {start_x} to {shifted}")
