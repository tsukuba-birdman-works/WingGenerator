import json
import numpy as np
from core.engine import RibGeneratorEngine
from shapely.geometry import Polygon

engine = RibGeneratorEngine()
u_x = np.linspace(0, 200, 200)
u_y = 10 * np.sin(np.pi * u_x / 200)
l_x = np.linspace(0, 200, 200)
l_y = -10 * np.sin(np.pi * l_x / 200)
pts = np.vstack([np.column_stack((u_x, u_y)), np.column_stack((l_x[::-1], l_y[::-1]))])
rib_poly = Polygon(pts)

poly, caps = engine.apply_te_caps(rib_poly, u_x, u_y, l_x, l_y,
                                  10.0, 2.0, 0, 0, np.eye(2),
                                  True, 5.0, False, 0.0,
                                  True, 5.0, False, 0.0)

print(caps[0])

