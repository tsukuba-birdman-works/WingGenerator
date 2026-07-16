from shapely.geometry import Polygon, LineString
from shapely.ops import split
import numpy as np

# Rib from x=0 (LE) to x=200 (TE)
# Thickness is 20mm in middle, tapering to 2mm at TE
x = np.linspace(0, 200, 100)
# TE is at x=200. te_cut = 20, so cut is at x=180.
y_u = 10 - x*0.04
y_l = -10 + x*0.04

u_pts = np.column_stack((x, y_u))
l_pts = np.column_stack((x[::-1], y_l[::-1]))
rib_poly = Polygon(np.vstack((u_pts, l_pts))).buffer(0)

print("Original rib area:", rib_poly.area)

te_start = 20.0 + 10.0 # 30mm from TE
# x coordinate for te_start: TE is 200, so 30mm from TE is 170.
# The cap is placed from 35mm from TE to 30.01mm from TE.
# So X goes from 165 to 169.99
# Let's create a groove_poly
f_w = 5.0
te_start = 30.0

groove_poly = Polygon([
    (200 - (te_start + f_w), 20),
    (200 - (te_start + 0.01), 20),
    (200 - (te_start + 0.01), y_u[85] - 1.0),
    (200 - (te_start + f_w), y_u[82] - 1.0)
]).buffer(0)

rib_poly_mod = rib_poly.difference(groove_poly)
print("After difference area:", rib_poly_mod.area)

# Now cut at te_start
P_u = np.array([200 - te_start, 20])
P_l = np.array([200 - te_start, -20])
line = LineString([P_u, P_l])

print("Cutting with line:", line)
splits = list(split(rib_poly_mod, line).geoms)
print("Splits count:", len(splits))

for i, p in enumerate(splits):
    print(f"Split {i} bounds:", p.bounds, "area:", p.area)

