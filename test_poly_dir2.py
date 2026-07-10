import sys
import os
sys.path.append(os.getcwd())
import numpy as np
from shapely.geometry import Polygon

poly = Polygon([(0,0), (-10,-1), (-10,1)]).buffer(0)
print("Is CCW:", poly.exterior.is_ccw)
print("Coords:", list(poly.exterior.coords))
