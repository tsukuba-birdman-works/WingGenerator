import numpy as np
import core.engine
from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import matplotlib.pyplot as plt

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
p = ui._get_builder_params()
p['file1'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['file2'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['wing_span'] = 1000.0
p['chord_root'] = 250.0
p['chord_tip'] = 200.0
p['spar_pos_root'] = 30.0
p['spar_pos_tip'] = 30.0
p['front_spar_dia'] = 8.0
p['front_spar_dx'] = -30.0

engine = ui.engine
chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = engine.get_local_params(p, 500)
pts1 = engine.load_dat(p['file1'])
n_pts = 300
blended = engine.resample_airfoil(pts1, n_pts)
scaled = blended * chord
le_idx = np.argmin(scaled[:, 0])
u_x_orig = scaled[:le_idx+1, 0][::-1]
u_y_orig = scaled[:le_idx+1, 1][::-1]
l_x_orig = scaled[le_idx:, 0]
l_y_orig = scaled[le_idx:, 1]

spar_x = chord * (spar_pct / 100.0)
spar_y = (float(np.interp(spar_x, u_x_orig, u_y_orig)) + float(np.interp(spar_x, l_x_orig, l_y_orig))) / 2.0

l_pts = np.column_stack((l_x_orig, l_y_orig))
u_pts = np.column_stack((u_x_orig, u_y_orig))
rib_poly_envelope = Polygon(np.vstack((u_pts, l_pts[::-1])))

R_m = p['spar_hole_dia'] / 2.0
R_f = p['front_spar_dia'] / 2.0
c_m = (spar_x, spar_y)
c_f = (spar_x - 30.0, spar_y)

base_y = spar_y - 100
base_top = base_y + 25
jig_angle = 80.0
jig_wall_thick = 10.0

pillars = []
for cx, cy, R in [(c_m[0], c_m[1], R_m), (c_f[0], c_f[1], R_f)]:
    top_y = cy + 0.2 * R
    bottom_y = cy - R - jig_wall_thick
    left = cx - R - jig_wall_thick
    right = cx + R + jig_wall_thick
    cradle_box = box(left, bottom_y, right, top_y)
    height = bottom_y - base_top
    if height > 0:
        dx = height / np.tan(np.radians(jig_angle))
        trap = Polygon([(left-dx, base_top), (right+dx, base_top), (right, bottom_y), (left, bottom_y)])
        pillars.append(unary_union([cradle_box, trap]))
    else:
        pillars.append(cradle_box)

# TE Support
max_lx = np.max(l_x_orig)
te_support_start_x = max_lx - 5.0 - 10.0
te_pts = []
for i in range(len(l_x_orig)):
    if l_x_orig[i] >= te_support_start_x and l_x_orig[i] <= max_lx:
        te_pts.append((l_x_orig[i], l_y_orig[i]))
if not te_pts: te_pts.append((l_x_orig[-1], l_y_orig[-1]))

last_x, last_y = te_pts[-1]
te_pts.append((last_x, last_y + 10.0))
te_pts.append((last_x + 5.0, last_y + 10.0))
te_pts.append((last_x + 5.0, base_top))
first_x, first_y = te_pts[0]
height_te = first_y - base_top
dx = height_te / np.tan(np.radians(jig_angle)) if height_te > 0 else 0
te_pts.append((first_x - dx, base_top))
pillars.append(Polygon(te_pts))

combined = unary_union(pillars)
min_x, min_y, max_x, max_y = combined.bounds
base_box = box(min_x - 10, base_y, max_x + 10, base_top)
jig_poly = unary_union([base_box, combined])

# PENETRATION PROCESSING
jig_poly = jig_poly.difference(rib_poly_envelope)

# 60% boxes
cutouts = [
    box(c_m[0] - 0.6*R_m, c_m[1] - R_m, c_m[0] + 0.6*R_m, c_m[1] + 0.2*R_m),
    box(c_f[0] - 0.6*R_f, c_f[1] - R_f, c_f[0] + 0.6*R_f, c_f[1] + 0.2*R_f)
]
jig_poly = jig_poly.difference(unary_union(cutouts))

# Plot
plt.figure()
if jig_poly.geom_type == 'Polygon':
    x, y = jig_poly.exterior.xy
    plt.plot(x, y, label='Jig')
elif jig_poly.geom_type == 'MultiPolygon':
    for g in jig_poly.geoms:
        x, y = g.exterior.xy
        plt.plot(x, y, label='Jig')

rx, ry = rib_poly_envelope.exterior.xy
plt.plot(rx, ry, 'k--', label='Rib')
plt.axis('equal')
plt.savefig('scratch/test_jig_smart2.png')
print("Saved")
