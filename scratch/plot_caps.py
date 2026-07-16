import numpy as np
import matplotlib.pyplot as plt
from core.engine import RibGeneratorEngine

class DotDict(dict):
    def __getattr__(self, key):
        return self.get(key, 0.0)

engine = RibGeneratorEngine()
p = DotDict({
    'chord': 200.0,
    'te_cut': 10.0,
    'uf_cap_act': True, 'uf_cap_w': 5.0,
    'lf_cap_act': True, 'lf_cap_w': 5.0,
    'ur_cap_act': False, 'ur_cap_w': 0.0,
    'lr_cap_act': False, 'lr_cap_w': 0.0,
    'te_cap_thick': 2.0
})

poly, u_x, u_y, l_x, l_y = engine.generate_base_airfoil(p)

poly, caps = engine.apply_te_caps(poly, u_x, u_y, l_x, l_y,
                                  p.te_cut, p.te_cap_thick, 50, 0, np.eye(2),
                                  p.uf_cap_act, p.uf_cap_w, p.ur_cap_act, p.ur_cap_w,
                                  p.lf_cap_act, p.lf_cap_w, p.lr_cap_act, p.lr_cap_w)

plt.figure(figsize=(12, 6))
if poly.geom_type == 'Polygon':
    plt.plot(*poly.exterior.xy, 'k-', label='Rib')
else:
    for geom in poly.geoms:
        plt.plot(*geom.exterior.xy, 'k-')

if caps and len(caps) >= 2:
    for cap_poly in caps[0]: # u_caps
        plt.plot(*cap_poly.exterior.xy, 'r-', linewidth=2, label='U Cap')
        plt.fill(*cap_poly.exterior.xy, 'r', alpha=0.3)
    for cap_poly in caps[1]: # l_caps
        plt.plot(*cap_poly.exterior.xy, 'b-', linewidth=2, label='L Cap')
        plt.fill(*cap_poly.exterior.xy, 'b', alpha=0.3)

# TE block spans from distance te_cut to te_cut + 10.0 from trailing edge.
# Trailing edge is at X=200 roughly. 
# But distance is arc length! Let's just plot it
plt.axvline(200 - p.te_cut - 10.0, color='g', linestyle='--', label='Approx TE Front')
plt.xlim(175, 195)
plt.ylim(-10, 10)
plt.legend()
plt.savefig('scratch/plot_caps.png')
print("Saved plot_caps.png")
