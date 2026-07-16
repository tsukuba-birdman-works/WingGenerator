import numpy as np
import matplotlib.pyplot as plt
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
                                  10.0, 2.0, 50, 0, np.eye(2),
                                  True, 5.0, False, 0.0,
                                  True, 5.0, False, 0.0)

plt.figure(figsize=(12, 6))
if poly.geom_type == 'Polygon':
    plt.plot(*poly.exterior.xy, 'k-', label='Rib')
else:
    for geom in poly.geoms:
        plt.plot(*geom.exterior.xy, 'k-')

if caps and len(caps) >= 2:
    for cap_pts in caps[0]: # u_caps
        p_c = Polygon(cap_pts)
        plt.plot(*p_c.exterior.xy, 'r-', linewidth=2, label='U Cap')
        plt.fill(*p_c.exterior.xy, 'r', alpha=0.3)
    for cap_pts in caps[1]: # l_caps
        p_c = Polygon(cap_pts)
        plt.plot(*p_c.exterior.xy, 'b-', linewidth=2, label='L Cap')
        plt.fill(*p_c.exterior.xy, 'b', alpha=0.3)

plt.axvline(200 - 20.0, color='g', linestyle='--', label='TE Front (dist=20)')
plt.xlim(170, 190)
plt.ylim(-5, 5)
plt.legend()
plt.savefig('scratch/plot_caps4.png')
print("Saved plot_caps4.png")

