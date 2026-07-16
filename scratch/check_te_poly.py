from core.engine import RibGeneratorEngine
import numpy as np
from shapely.geometry import Polygon

engine = RibGeneratorEngine()

# Simulate a rib polygon from LE to TE cut
x = np.linspace(0, 180, 100) # LE to te_cut (180)
y_u = 10 - x*0.04
y_l = -10 + x*0.04

u_pts = np.column_stack((x, y_u))
l_pts = np.column_stack((x[::-1], y_l[::-1]))
final_rib_mod_poly = Polygon(np.vstack((u_pts, l_pts))).buffer(0)

# Simulate apply_te_caps notch
# cap is from 165 to 169.99
groove_poly = Polygon([(165, 20), (169.99, 20), (169.99, 0), (165, 0)]).buffer(0)
final_rib_mod_poly = final_rib_mod_poly.difference(groove_poly)

# cut te_poly
# te_start = 170.0
P_u_rot_te = np.array([170.0, 20])
P_l_rot_te = np.array([170.0, -20])

te_poly = engine.cut_polygon_by_line(final_rib_mod_poly, P_u_rot_te, P_l_rot_te, 'right')
print("TE Poly is None?", te_poly is None)
if te_poly:
    print("TE Poly is empty?", te_poly.is_empty)
    print("TE Poly area:", te_poly.area)
    print("Centroid:", te_poly.centroid.x)

