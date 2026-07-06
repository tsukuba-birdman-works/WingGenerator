import numpy as np

def generate_jig_at_y_new(self, p, y_local: float):
    from shapely.geometry import Polygon, LineString, Point, box
    from shapely.ops import unary_union
    
    chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = self.get_local_params(p, y_local)
    
    if p['wing_span'] > 0:
        t = y_local / p['wing_span']
    else:
        t = 0
        
    te_cut = float(p.get('te_cut', 0.0))
    d_m = p.get('spar_hole_dia', 10.0)
    d_r = p.get('rear_spar_dia', 8.0)
    R_m = d_m / 2.0
    R_r = d_r / 2.0
    
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
        return None

    # Spar centers (UNROTATED)
    spar_x = chord * (spar_pct / 100.0)
    spar_y = (float(np.interp(spar_x, u_x_orig, u_y_orig)) + float(np.interp(spar_x, l_x_orig, l_y_orig))) / 2.0
    
    rear_dx = float(p.get('rear_spar_dx', 0.0))
    rear_dy = float(p.get('rear_spar_dy', 0.0))
    rear_x_unrot = spar_x + rear_dx
    rear_y_unrot = spar_y + rear_dy
    
    # Apply washout rotation exactly like generate_single_rib
    w_theta = np.radians(washout)
    R_mat = np.array([[np.cos(w_theta), -np.sin(w_theta)], [np.sin(w_theta), np.cos(w_theta)]])
    
    l_pts = np.column_stack((l_x_orig, l_y_orig))
    rot_l_pts = (l_pts - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
    l_x = rot_l_pts[:, 0]
    l_y = rot_l_pts[:, 1]
    
    # Rotated spar centers
    spar_x_rot = spar_x
    spar_y_rot = spar_y
    c_r_rot = (np.array([rear_x_unrot, rear_y_unrot]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
    rear_spar_x_rot = c_r_rot[0]
    rear_spar_y_rot = c_r_rot[1]
    
    base_height = float(p.get('jig_base_height', 100.0))
    slot_interval = float(p.get('jig_slot_interval', 100.0))
    slot_width = float(p.get('jig_slot_width', 3.0))
    slot_depth = float(p.get('jig_slot_depth', 10.0))
    
    base_y = spar_y_rot - base_height
    
    fm_left = spar_x_rot - R_m
    fm_right = spar_x_rot + R_m
    fm_bottom = spar_y_rot - R_m
    fm_top = spar_y_rot + 0.2 * R_m
    
    rm_left = rear_spar_x_rot - R_r
    rm_right = rear_spar_x_rot + R_r
    rm_bottom = rear_spar_y_rot - R_r
    rm_top = rear_spar_y_rot + 0.2 * R_r
    
    te_support_start_x = chord - te_cut - 10.0
    
    if te_support_start_x >= chord:
        te_support_start_x = chord - 10.0
    if te_support_start_x <= rm_right + 5.0:
        te_support_start_x = rm_right + 5.0

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
            
    if not te_x_arr:
        te_x_arr.append(l_x[-1])
        te_y_arr.append(l_y[-1])
        
    for x, y in zip(te_x_arr, te_y_arr):
        pts.append((x, y))
        
    last_x, last_y = te_x_arr[-1], te_y_arr[-1]
    pts.append((last_x, base_y))
    
    poly = Polygon(pts)
    poly = poly.buffer(0)
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
