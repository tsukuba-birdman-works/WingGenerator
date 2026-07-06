import re

with open("core/engine.py", "r") as f:
    content = f.read()

# Locate the function def
start_str = "    def generate_jig_at_y(self, p, y_local: float, return_full=False):"
# The next method is `export_dxf` or something?
end_str = "    def export_dxf(self"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find function bounds!")
    import sys; sys.exit(1)

new_func = """    def generate_jig_at_y(self, p, y_local: float, return_full=False):
        from shapely.geometry import Polygon, LineString, Point, box
        from shapely.ops import unary_union
        import numpy as np

        chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = self.get_local_params(p, y_local)

        if p['wing_span'] > 0:
            t = y_local / p['wing_span']
        else:
            t = 0

        te_cut = float(p.get('te_cut', 0.0))
        d_f = float(p.get('front_spar_dia', 0.0))
        d_m = float(p.get('spar_hole_dia', 10.0))
        d_r = float(p.get('rear_spar_dia', 8.0))

        front_dx = float(p.get('front_spar_dx', 0.0))
        front_dy = float(p.get('front_spar_dy', 0.0))
        rear_dx = float(p.get('rear_spar_dx', 0.0))
        rear_dy = float(p.get('rear_spar_dy', 0.0))

        R_f = d_f / 2.0
        R_m = d_m / 2.0
        R_r = d_r / 2.0

        jig_base_height = float(p.get('jig_base_height', 100.0))
        jig_base_thick = float(p.get('jig_base_thickness', 25.0))
        jig_wall_thick = float(p.get('jig_wall_thickness', 10.0))
        jig_angle = float(p.get('jig_pillar_angle', 90.0))
        jig_te_stopper = float(p.get('jig_te_stopper_height', 10.0))

        slot_interval = float(p.get('jig_slot_interval', 100.0))
        slot_width = float(p.get('jig_slot_width', 3.0))
        slot_depth = float(p.get('jig_slot_depth', 10.0))

        try:
            pts1 = self.load_dat(p['file1'])
            pts2 = self.load_dat(p['file2'])

            n_pts = 300
            blended = self.resample_airfoil(pts1, n_pts) * (1.0 - t) + self.resample_airfoil(pts2, n_pts) * t
            scaled = blended * chord

            le_idx = np.argmin(scaled[:, 0])
            u_x_orig = scaled[:le_idx+1, 0][::-1]
            u_y_orig = scaled[:le_idx+1, 1][::-1]
            l_x_orig = scaled[le_idx:, 0]
            l_y_orig = scaled[le_idx:, 1]
        except Exception as e:
            print(f"Jig generation error at Y={y_local}: {e}")
            if return_full: return {}
            return None

        spar_x = chord * (spar_pct / 100.0)
        spar_y = (float(np.interp(spar_x, u_x_orig, u_y_orig)) + float(np.interp(spar_x, l_x_orig, l_y_orig))) / 2.0

        w_theta = np.radians(washout)
        R_mat = np.array([[np.cos(w_theta), -np.sin(w_theta)], [np.sin(w_theta), np.cos(w_theta)]])

        l_pts = np.column_stack((l_x_orig, l_y_orig))
        rot_l_pts = (l_pts - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        l_x = rot_l_pts[:, 0]
        l_y = rot_l_pts[:, 1]
        
        rot_u_pts = (np.column_stack((u_x_orig, u_y_orig)) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        wing_pts = np.vstack((rot_u_pts, rot_l_pts[::-1])).tolist()
        rib_poly = Polygon(wing_pts)

        spar_x_rot = spar_x
        spar_y_rot = spar_y

        c_f_rot = (np.array([spar_x + front_dx, spar_y + front_dy]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        front_spar_x_rot, front_spar_y_rot = c_f_rot[0], c_f_rot[1]

        c_r_rot = (np.array([spar_x + rear_dx, spar_y + rear_dy]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        rear_spar_x_rot, rear_spar_y_rot = c_r_rot[0], c_r_rot[1]

        base_y = spar_y_rot - jig_base_height
        base_top = base_y + jig_base_thick

        def make_spar_pillar(cx, cy, R):
            top_y = cy + 0.2 * R
            bottom_y = cy - R - jig_wall_thick
            left = cx - R - jig_wall_thick
            right = cx + R + jig_wall_thick
            cradle_box = box(left, bottom_y, right, top_y)

            height = bottom_y - base_top
            if height > 0:
                dx = height / np.tan(np.radians(jig_angle)) if jig_angle not in (0, 90) else 0
                trap_pts = [
                    (left - dx, base_top),
                    (right + dx, base_top),
                    (right, bottom_y),
                    (left, bottom_y)
                ]
                return unary_union([cradle_box, Polygon(trap_pts)])
            return cradle_box

        pillars = []
        pillars.append(make_spar_pillar(spar_x_rot, spar_y_rot, R_m))
        if d_f > 0: pillars.append(make_spar_pillar(front_spar_x_rot, front_spar_y_rot, R_f))
        if d_r > 0: pillars.append(make_spar_pillar(rear_spar_x_rot, rear_spar_y_rot, R_r))

        max_lx = np.max(l_x)
        te_support_start_x = max_lx - te_cut - 10.0
        if d_r > 0:
            rm_right = rear_spar_x_rot + R_r + jig_wall_thick
            if te_support_start_x <= rm_right + 5.0:
                te_support_start_x = rm_right + 5.0

        te_x_arr = []
        te_y_arr = []
        for i in range(len(l_x)):
            if l_x[i] >= te_support_start_x and l_x[i] <= max_lx:
                te_x_arr.append(l_x[i])
                te_y_arr.append(l_y[i])

        if not te_x_arr:
            te_x_arr.append(l_x[-1])
            te_y_arr.append(l_y[-1])

        te_pts = []
        for x, y in zip(te_x_arr, te_y_arr):
            te_pts.append((x, y))

        last_x, last_y = te_pts[-1]
        te_pts.append((last_x, last_y + jig_te_stopper))
        te_pts.append((last_x + 5.0, last_y + jig_te_stopper))
        te_pts.append((last_x + 5.0, base_top))

        first_x, first_y = te_pts[0]
        height_te = first_y - base_top
        if height_te > 0:
            dx = height_te / np.tan(np.radians(jig_angle)) if jig_angle not in (0, 90) else 0
        else:
            dx = 0
        te_pts.append((first_x - dx, base_top))

        te_poly = Polygon(te_pts)
        pillars.append(te_poly)

        combined = unary_union(pillars)
        min_x, min_y, max_x, max_y = combined.bounds

        base_box = box(min_x - 10.0, base_y, max_x + 10.0, base_top)

        jig_poly = unary_union([base_box, combined])

        # Subtract Rib for embedment processing
        jig_poly = jig_poly.difference(rib_poly)

        holes = []
        # Box cutouts for spars (60% of diameter width)
        box_w_m = 0.6 * d_m
        holes.append(box(spar_x_rot - box_w_m/2, spar_y_rot - R_m, spar_x_rot + box_w_m/2, spar_y_rot + R_m))
        if d_f > 0:
            box_w_f = 0.6 * d_f
            holes.append(box(front_spar_x_rot - box_w_f/2, front_spar_y_rot - R_f, front_spar_x_rot + box_w_f/2, front_spar_y_rot + R_f))
        if d_r > 0:
            box_w_r = 0.6 * d_r
            holes.append(box(rear_spar_x_rot - box_w_r/2, rear_spar_y_rot - R_r, rear_spar_x_rot + box_w_r/2, rear_spar_y_rot + R_r))

        jig_poly = jig_poly.difference(unary_union(holes))

        # Two slots centered around smallest rib center
        c_tip = float(p.get('chord_tip', 200.0)) / 2.0
        x1 = c_tip - slot_interval / 2.0
        x2 = c_tip + slot_interval / 2.0
        sb1 = box(x1 - slot_width/2.0, base_y - 1.0, x1 + slot_width/2.0, base_y + slot_depth)
        sb2 = box(x2 - slot_width/2.0, base_y - 1.0, x2 + slot_width/2.0, base_y + slot_depth)
        jig_poly = jig_poly.difference(unary_union([sb1, sb2]))

        if jig_poly.geom_type == 'Polygon':
            jig_pts_out = list(jig_poly.exterior.coords)
        elif jig_poly.geom_type == 'MultiPolygon':
            largest = max(jig_poly.geoms, key=lambda g: g.area)
            jig_pts_out = list(largest.exterior.coords)
        else:
            jig_pts_out = []

        if return_full:
            return {
                'jig_pts': jig_pts_out,
                'wing_pts': wing_pts,
                'c_m': (spar_x_rot, spar_y_rot),
                'd_m': d_m,
                'c_f': (front_spar_x_rot, front_spar_y_rot),
                'd_f': d_f,
                'c_r': (rear_spar_x_rot, rear_spar_y_rot),
                'd_r': d_r
            }
        return jig_pts_out
"""

new_content = content[:start_idx] + new_func + "\n" + content[end_idx:]

with open("core/engine.py", "w") as f:
    f.write(new_content)

print("engine.py patched successfully")
