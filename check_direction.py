from shapely.geometry import Polygon
import numpy as np

# A simple square
poly = Polygon([(0,0), (10,0), (10,10), (0,10)])
out_poly = poly.buffer(1.0)

def is_ccw(coords):
    area = 0
    for i in range(len(coords)-1):
        area += (coords[i+1][0] - coords[i][0]) * (coords[i+1][1] + coords[i][1])
    return area < 0

print("Original exterior CCW:", is_ccw(list(poly.exterior.coords)))
print("Buffered exterior CCW:", is_ccw(list(out_poly.exterior.coords)))

hole_poly = Polygon([(0,0), (10,0), (10,10), (0,10)], [[(2,2), (2,8), (8,8), (8,2)]])
print("Hole interior CCW:", is_ccw(list(hole_poly.interiors[0].coords)))
