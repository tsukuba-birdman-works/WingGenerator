from shapely.geometry import Polygon
import numpy as np

def is_ccw(coords):
    area = 0
    for i in range(len(coords)-1):
        area += (coords[i+1][0] - coords[i][0]) * (coords[i+1][1] + coords[i][1])
    return area < 0

truss_hole = Polygon([(20,20), (80,20), (50,80)])
print("Original truss hole CCW:", is_ccw(list(truss_hole.exterior.coords)))

buffered = truss_hole.buffer(-2.0)
print("Buffered inner CCW:", is_ccw(list(buffered.exterior.coords)))
