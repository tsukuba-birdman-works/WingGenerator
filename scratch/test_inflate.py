from shapely.geometry import Polygon, box
import numpy as np

# Simple triangle: LE at 0, TE at 100
poly = Polygon([(0,0), (100, 5), (100, -5)])

inflated = poly.buffer(1.0)
print("Original bounds:", poly.bounds)
print("Inflated bounds:", inflated.bounds)

# Cut off the extra X
bbox = box(poly.bounds[0], -999, poly.bounds[2], 999)
inflated_cut = inflated.intersection(bbox)
print("Inflated cut bounds:", inflated_cut.bounds)
