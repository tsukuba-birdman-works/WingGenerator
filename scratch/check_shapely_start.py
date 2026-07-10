from shapely.geometry import Polygon, LineString
from shapely.ops import split
import numpy as np

poly = Polygon([(200,0), (180, 10), (100, 10), (100, -10), (180, -10)])
line = LineString([(180, 20), (180, -20)])
result = split(poly, line)
for g in result.geoms:
    if g.centroid.x > 150: # The right side
        print("Shapely start point:")
        print(np.array(g.exterior.coords)[0])
        print("Shapely full coords:")
        print(np.array(g.exterior.coords))
