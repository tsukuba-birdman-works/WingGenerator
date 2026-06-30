from shapely.geometry import Polygon
import numpy as np

def is_ccw(coords):
    area = 0
    for i in range(len(coords)-1):
        area += (coords[i+1][0] - coords[i][0]) * (coords[i+1][1] + coords[i][1])
    return area < 0

# Hole definition (e.g. from engine.py final_truss_holes)
# In engine, holes are usually difference from the main rib, so they are interiors, or just generated as Polygons.
# If generated as a list of points e.g. [(20,20), (80,20), (50,80), (20,20)]
hole_pts = [(20,20), (80,20), (50,80), (20,20)]
print("Original hole CCW:", is_ccw(hole_pts))

h_poly = Polygon(hole_pts)
h_offset = h_poly.buffer(-2.0)
print("Offset hole CCW:", is_ccw(list(h_offset.exterior.coords)))

# Bolt hole
pts = [(10 + 5 * np.cos(t), 10 + 5 * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
print("Bolt hole CCW:", is_ccw(pts))
