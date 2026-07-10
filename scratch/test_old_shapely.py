from shapely.geometry import Polygon, LineString
from shapely.ops import split
import numpy as np

# A typical airfoil offset polygon
# LE at (0,0), TE at (200,0)
# Top curve goes from LE to TE.
# So TE to LE goes backwards.
poly_coords = [
    (0,0), (10, 5), (100, 15), (190, 5), (200,0), # Lower? No, LE to TE (Upper)
    (190, -5), (100, -15), (10, -5), (0,0)        # Lower
]
# Wait, Shapely CCW:
# TE (200,0) -> Upper -> LE (0,0) -> Lower -> TE (200,0)
# (200,0) -> (190, 5) -> (100, 15) -> (10, 5) -> (0,0) -> (10, -5) -> (100, -15) -> (190, -5) -> (200,0)
poly_coords = [
    (200,0), (190, 5), (100, 15), (10, 5), (0,0),
    (10, -5), (100, -15), (190, -5), (200,0)
]
poly = Polygon(poly_coords).buffer(0)

P_u = (180, 10)
P_l = (180, -10)
vec = np.array(P_l) - np.array(P_u)
vec = vec / np.linalg.norm(vec)
line = LineString([np.array(P_u) - vec*1000, np.array(P_l) + vec*1000])

result = split(poly, line)
geoms = list(result.geoms)
best_poly, best_val = None, -float('inf')
for g in geoms:
    if g.centroid.x > best_val:
        best_val, best_poly = g.centroid.x, g

old_coords = np.array(best_poly.exterior.coords)
print("Old Shapely order:")
print(old_coords[:4])
print("...")

# My manual array for the same shape:
# TE -> Upper Cut -> Lower Cut -> TE
# TE=(200,0). Upper cut=(180, 4.4). Lower cut=(180, -4.4).
print("\nMy manual order (TE -> Upper Cut -> Lower Cut -> TE):")
print(np.array([[200,0], [190, 5], [180, 4.4], [180, -4.4], [190, -5], [200,0]]))
