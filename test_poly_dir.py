import sys
import os
sys.path.append(os.getcwd())
import numpy as np
from shapely.geometry import Polygon

# create a typical TE poly: triangle from (0,0) [TE] to (-10,-1) [bottom] to (-10,1) [top]
poly = Polygon([(0,0), (-10,-1), (-10,1)])
print("Is CCW:", poly.exterior.is_ccw)
print("Coords:", list(poly.exterior.coords))
