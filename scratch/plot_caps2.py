import json
import matplotlib.pyplot as plt
from core.engine import RibGeneratorEngine
import copy

engine = RibGeneratorEngine()
with open("preset/test.json", "r") as f:
    p = json.load(f)

# Modify te_cut and cap to ensure we see it clearly
p['te_cut'] = 10.0
p['uf_cap_act'] = True
p['uf_cap_w'] = 5.0
p['lf_cap_act'] = True
p['lf_cap_w'] = 5.0
p['te_cap_thick'] = 2.0

res = engine.generate_rib_at_y(p, 0, 0, 2.0)
poly, l_x, l_y, u_x, u_y = res[0], res[1], res[2], res[3], res[4]
# res structure: rib_poly, u_x, u_y, l_x, l_y, cap_pts, ...

print(len(res))
# Let's just find the cap_pts in the result
caps = res[5]

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

plt.axvline(200 - 10.0 - 10.0, color='g', linestyle='--', label='Approx TE Front')
plt.xlim(175, 195)
plt.ylim(-10, 10)
plt.legend()
plt.savefig('scratch/plot_caps2.png')
print("Saved plot_caps2.png")

