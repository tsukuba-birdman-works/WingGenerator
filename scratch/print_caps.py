import json
import numpy as np
from core.engine import RibGeneratorEngine
from shapely.geometry import Polygon

engine = RibGeneratorEngine()
with open("preset/test.json", "r") as f:
    p = json.load(f)

u_x = np.linspace(0, 200, 200)
u_y = 10 * np.sin(np.pi * u_x / 200)
l_x = np.linspace(0, 200, 200)
l_y = -10 * np.sin(np.pi * l_x / 200)
pts = np.vstack([np.column_stack((u_x, u_y)), np.column_stack((l_x[::-1], l_y[::-1]))])
rib_poly = Polygon(pts)

poly, caps = engine.apply_te_caps(rib_poly, u_x, u_y, l_x, l_y,
                                  10.0, 2.0, 50, 0, np.eye(2),
                                  True, 5.0, False, 0.0,
                                  True, 5.0, False, 0.0)

print("TE Block Front Face X (approx):", 200 - 20)
if caps and len(caps) >= 2:
    for i, cap_pts in enumerate(caps):
        p_c = Polygon(cap_pts)
        min_x, min_y, max_x, max_y = p_c.bounds
        print(f"Cap {i} bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")

