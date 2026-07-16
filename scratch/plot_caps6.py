import numpy as np
import matplotlib.pyplot as plt
from core.engine import RibGeneratorEngine
from shapely.geometry import Polygon

class FixedEngine(RibGeneratorEngine):
    def apply_te_caps(self, rib_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig, te_cut, cap_thick, spar_x, spar_y, R_mat,
                      uf_act, uf_w, ur_act, ur_w, lf_act, lf_w, lr_act, lr_w):
        u_pts_rev = np.column_stack((u_x_orig[::-1], u_y_orig[::-1]))
        dist_u = np.zeros(len(u_pts_rev))
        dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))

        l_pts_rev = np.column_stack((l_x_orig[::-1], l_y_orig[::-1]))
        dist_l = np.zeros(len(l_pts_rev))
        dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))

        groove_polys = []
        cap_pts_list = []

        te_start = te_cut + 10.0
        t = max(cap_thick, 0.1) if cap_thick > 0 else 0.1

        def build_cap(pts_rev, dist_arr, is_upper):
            f_act = uf_act if is_upper else lf_act
            f_w = uf_w if is_upper else lf_w
            r_act = ur_act if is_upper else lr_act
            r_w = ur_w if is_upper else lr_w

            zones = []
            if f_act and f_w > 0: zones.append((te_start + f_w, te_start + 0.01, True))
            if r_act and r_w > 0: zones.append((r_w, 0.0, False))

            for start_d, end_d, is_front in zones:
                if start_d <= 0 or start_d <= end_d: continue

                p_start = np.array([np.interp(start_d, dist_arr, pts_rev[:, 0]), np.interp(start_d, dist_arr, pts_rev[:, 1])])
                p_end = np.array([np.interp(end_d, dist_arr, pts_rev[:, 0]), np.interp(end_d, dist_arr, pts_rev[:, 1])])

                mask = (dist_arr < start_d) & (dist_arr > end_d)
                inner_pts = pts_rev[mask][::-1]  # <--- FIX HERE

                surf_pts = [p_start]
                if len(inner_pts) > 0: surf_pts.extend(inner_pts)
                surf_pts.append(p_end)
                surf_pts = np.array(surf_pts)

                n_pts = len(surf_pts)
                in_bound, out_bound, cap_surf = [], [], []
                eps_out = 5.0

                for i in range(n_pts):
                    p = surf_pts[i]
                    if i < n_pts - 1: v = surf_pts[i+1] - p
                    else: v = p - surf_pts[i-1]

                    n = np.array([-v[1], v[0]])
                    n = n / np.linalg.norm(n) if np.linalg.norm(n) > 0 else np.array([0, 1])

                    if is_upper: n = -n if n[1] < 0 else n
                    else: n = -n if n[1] > 0 else n

                    if is_front and cap_thick > 0:
                        in_bound.append(p - n * cap_thick)
                        cap_surf.append(p)
                    else:
                        in_bound.append(p + n * 0.1)
                        cap_surf.append(p + n * (0.1 + t))

                    out_bound.append(p + n * eps_out)

                rot_pts = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in in_bound + out_bound[::-1]]
                cap_geom = cap_surf + in_bound[::-1]
                rot_cap = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in cap_geom]
                cap_pts_list.append(np.array(rot_cap))

        build_cap(u_pts_rev, dist_u, True); build_cap(l_pts_rev, dist_l, False)
        return rib_poly, cap_pts_list

engine = FixedEngine()
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

colors = ['r', 'b', 'g', 'm']
if caps:
    for i, cap_pts in enumerate(caps):
        p_c = Polygon(cap_pts)
        plt.plot(*p_c.exterior.xy, colors[i%4]+'-', linewidth=2, label=f'Cap {i}')
        plt.fill(*p_c.exterior.xy, colors[i%4], alpha=0.3)

plt.axvline(200 - 20.0, color='g', linestyle='--', label='TE Front (dist=20)')
plt.xlim(170, 190)
plt.ylim(-5, 5)
plt.legend()
plt.savefig('scratch/plot_caps6.png')
print("Saved plot_caps6.png")
for i, cap_pts in enumerate(caps):
    p_c = Polygon(cap_pts)
    min_x, min_y, max_x, max_y = p_c.bounds
    print(f"Fixed Cap {i} bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")
