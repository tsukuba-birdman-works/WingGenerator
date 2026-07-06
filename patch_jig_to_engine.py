import sys
with open('core/engine.py', 'r') as f:
    lines = f.readlines()

jig_code = """
    def generate_jig_at_y(self, p, y_local: float, return_full=False):
        import numpy as np
        from shapely.geometry import Polygon, box, Point, LineString
        from shapely.ops import unary_union

        chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = self.get_local_params(p, y_local)

        if p['wing_span'] > 0:
            t = y_local / p['wing_span']
        else:
            t = 0

        te_cut = p['te_cut']
        d_m = p['d_m']
        d_r = p['d_r']
        R_m = d_m / 2.0
        R_r = d_r / 2.0

        try:
            raw_curve = self.get_slice_curve(self.x_all, self.y_all, self.s_all, 100, 100, t, t)
            pts = self.resample_airfoil(raw_curve, 300)
            u_x, u_y, l_x, l_y = self.split_airfoil(pts)
        except Exception as e:
            print(f"Jig generation error at Y={y_local}: {e}")
            return None

        if washout != 0.0:
            theta = np.radians(washout)
            c, s = np.cos(theta), np.sin(theta)

            rot_u_x = c * u_x - s * u_y
            rot_u_y = s * u_x + c * u_y
            rot_l_x = c * l_x - s * l_y
            rot_l_y = s * l_x + c * l_y

            u_x, u_y = rot_u_x, rot_u_y
            l_x, l_y = rot_l_x, rot_l_y

        spar_x = chord * spar_pct / 100.0
        spar_y = self.find_intersection(spar_x, 0, 90, l_x, l_y, "up")
        if spar_y is None: spar_y = 0.0

        rear_spar_x = chord * p['rear_spar_pos'] / 100.0
        rear_spar_y = self.find_intersection(rear_spar_x, 0, 90, l_x, l_y, "up")
        if rear_spar_y is None: rear_spar_y = 0.0

        base_height = p.get('jig_base_height', 100.0)
        slot_interval = p.get('jig_slot_interval', 100.0)
        slot_width = p.get('jig_slot_width', 3.0)
        slot_depth = p.get('jig_slot_depth', 10.0)

        base_y = spar_y - base_height

        fm_left = spar_x - R_m
        fm_right = spar_x + R_m
        fm_bottom = spar_y - R_m
        fm_top = spar_y + 0.2 * R_m

        rm_left = rear_spar_x - R_r
        rm_right = rear_spar_x + R_r
        rm_bottom = rear_spar_y - R_r
        rm_top = rear_spar_y + 0.2 * R_r

        te_support_start_x = chord - te_cut - 10.0

        pts = []
        pts.append((fm_left - 10.0, base_y))
        pts.append((fm_left - 10.0, fm_top))
        pts.append((fm_left, fm_top))
        pts.append((fm_left, fm_bottom))
        pts.append((fm_right, fm_bottom))
        pts.append((fm_right, fm_top))

        pts.append((rm_left, rm_top))
        pts.append((rm_left, rm_bottom))
        pts.append((rm_right, rm_bottom))
        pts.append((rm_right, rm_top))

        te_start_y = None
        for i in range(len(l_x)-1):
            if l_x[i] <= te_support_start_x <= l_x[i+1]:
                t_interp = (te_support_start_x - l_x[i]) / (l_x[i+1] - l_x[i]) if l_x[i+1] != l_x[i] else 0
                te_start_y = l_y[i] + t_interp * (l_y[i+1] - l_y[i])
                break
        if te_start_y is None:
            te_start_y = l_y[-1]

        pts.append((te_support_start_x, te_start_y))

        te_x_arr = []
        te_y_arr = []
        for i in range(len(l_x)):
            if l_x[i] >= te_support_start_x and l_x[i] <= chord:
                te_x_arr.append(l_x[i])
                te_y_arr.append(l_y[i])

        for x, y in zip(te_x_arr, te_y_arr):
            pts.append((x, y))

        last_x, last_y = te_x_arr[-1], te_y_arr[-1]
        pts.append((last_x, base_y))

        poly = Polygon(pts)
        min_x = fm_left - 10.0
        max_x = last_x

        slot_boxes = []
        x_curr = 0.0
        while x_curr <= max_x:
            if x_curr >= min_x:
                sb = box(x_curr - slot_width/2.0, base_y - 1.0, x_curr + slot_width/2.0, base_y + slot_depth)
                slot_boxes.append(sb)
            x_curr += slot_interval

        if slot_boxes:
            slots_union = unary_union(slot_boxes)
            poly = poly.difference(slots_union)

        if poly.geom_type == 'Polygon':
            return list(poly.exterior.coords)
        elif poly.geom_type == 'MultiPolygon':
            largest = max(poly.geoms, key=lambda g: g.area)
            return list(largest.exterior.coords)
        return []
"""

lines.append(jig_code)
with open('core/engine.py', 'w') as f:
    f.writelines(lines)
