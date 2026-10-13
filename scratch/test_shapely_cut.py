from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import numpy as np

# 1. Test notch (circle overlapping edge)
poly = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
cutter = Point(100, 25).buffer(10)
diff = poly.difference(cutter)
print("Notch diff type:", diff.geom_type)
print("Exterior points count:", len(diff.exterior.coords))
print("Interiors count:", len(diff.interiors))

# 2. Test internal hole (circle completely inside)
cutter_in = Point(50, 25).buffer(10)
diff_in = poly.difference(cutter_in)
print("Internal hole diff type:", diff_in.geom_type)
print("Exterior points count:", len(diff_in.exterior.coords))
print("Interiors count:", len(diff_in.interiors))
print("Interior coords count:", len(diff_in.interiors[0].coords))

# 3. Test slanted stadium cutter
stadium = LineString([(40, 20), (60, 30)]).buffer(5)
diff_stadium = poly.difference(stadium)
print("Stadium diff type:", diff_stadium.geom_type)
print("Stadium interiors count:", len(diff_stadium.interiors))
