    def generate_jig_at_y(self, p, y_local: float):
        import numpy as np
        from shapely.geometry import Polygon, box, Point, LineString
        from shapely.ops import unary_union
        
        chord, spar_pct, washout, t, xb_t_list, x_dia = self.get_local_params(p, y_local)
        
        te_cut = p.get('te_cut', 0.0)
        d_m = p.get('spar_hole_dia', 0.0)
        d_r = p.get('rear_spar_dia', 0.0)
        d_f = p.get('front_spar_dia', 0.0)
        
        front_dx = p.get('front_spar_dx', 0.0)
        front_dy = p.get('front_spar_dy', 0.0)
        rear_dx = p.get('rear_spar_dx', 0.0)
        rear_dy = p.get('rear_spar_dy', 0.0)
        
        try:
            pts1 = self.load_dat(p.get('file1', ''))
            pts2 = self.load_dat(p.get('file2', ''))
            if len(pts1) == 0 or len(pts2) == 0:
                print(f"Jig generation error at Y={y_local}: Missing valid dat files")
                return None
                
            n_pts = 300
            blended = self.resample_airfoil(pts1, n_pts) * (1.0 - t) + self.resample_airfoil(pts2, n_pts) * t
            scaled = blended * chord
            
            le_idx = np.argmin(scaled[:, 0])
            u_x_orig, u_y_orig = scaled[:le_idx+1, 0][::-1], scaled[:le_idx+1, 1][::-1]
            l_x_orig, l_y_orig = scaled[le_idx:, 0], scaled[le_idx:, 1]

            spar_x = chord * (spar_pct / 100.0)
            spar_y_pre = (np.interp(spar_x, u_x_orig, u_y_orig) + np.interp(spar_x, l_x_orig, l_y_orig)) / 2.0

            w_theta = np.radians(washout)
            R_mat = np.array([[np.cos(w_theta), -np.sin(w_theta)], [np.sin(w_theta), np.cos(w_theta)]])

            rotated = (scaled - [spar_x, spar_y_pre]).dot(R_mat.T) + [spar_x, spar_y_pre]

            le_idx = np.argmin(rotated[:, 0])
            u_x, u_y = rotated[:le_idx+1, 0][::-1], rotated[:le_idx+1, 1][::-1]
            l_x, l_y = rotated[le_idx:, 0], rotated[le_idx:, 1]
            
            c_m = np.array([spar_x, spar_y_pre])
            c_r = (np.array([spar_x + rear_dx, spar_y_pre + rear_dy]) - c_m).dot(R_mat.T) + c_m
            c_f = (np.array([spar_x + front_dx, spar_y_pre + front_dy]) - c_m).dot(R_mat.T) + c_m
            
        except Exception as e:
            print(f"Jig generation error at Y={y_local}: {e}")
            return None

        base_height = p.get('jig_base_height', 100.0)
        base_y = c_m[1] - base_height
        
        # TE Support range
        te_support_end_x = chord - te_cut
        te_support_start_x = te_support_end_x - 10.0
        
        # We need the lowest Y on the TE support to place the pillar
        te_pillar_x = te_support_end_x - 5.0
        sort_idx = np.argsort(l_x)
        te_pillar_y = np.interp(te_pillar_x, l_x[sort_idx], l_y[sort_idx])
        
        slot_interval = p.get('jig_slot_interval', 100.0)
        c_tip = float(p.get('chord_tip', 200.0)) / 2.0
        slot1_x = c_tip - slot_interval / 2.0
        slot2_x = c_tip + slot_interval / 2.0
        
        base_start_x = min(c_f[0] if d_f > 0 else c_m[0], slot1_x) - 15.0
        base_end_x = max(te_pillar_x, slot2_x) + 15.0
        
        # Create Skeleton Lines
        lines = []
        lines.append(LineString([(base_start_x, base_y), (base_end_x, base_y)]))
        
        if d_f > 0: lines.append(LineString([(c_f[0], base_y), (c_f[0], c_f[1])]))
        if d_m > 0: lines.append(LineString([(c_m[0], base_y), (c_m[0], c_m[1])]))
        if d_r > 0: lines.append(LineString([(c_r[0], base_y), (c_r[0], c_r[1])]))
        lines.append(LineString([(te_pillar_x, base_y), (te_pillar_x, te_pillar_y)]))
        
        # Diagonals for rigidity
        if d_f > 0 and d_m > 0:
            lines.append(LineString([(c_f[0], base_y), (c_m[0], c_m[1])]))
        if d_m > 0 and d_r > 0:
            lines.append(LineString([(c_m[0], base_y), (c_r[0], c_r[1])]))
        if d_r > 0:
            lines.append(LineString([(c_r[0], base_y), (te_pillar_x, te_pillar_y)]))
            
        # Buffer to make a frame (12mm width = 6mm buffer)
        frame_width = 12.0
        frame = unary_union(lines).buffer(frame_width / 2.0, cap_style=2, join_style=2)
        
        # Make base flat
        bottom_cut = box(base_start_x - 50, base_y - 50, base_end_x + 50, base_y)
        frame = frame.difference(bottom_cut)
        
        # First add the precise TE support pad
        te_x_arr, te_y_arr = [], []
        for xi, yi in zip(l_x, l_y):
            if te_support_start_x <= xi <= te_support_end_x:
                te_x_arr.append(xi)
                te_y_arr.append(yi)
        if len(te_x_arr) >= 2:
            te_pad_pts = [(te_support_start_x, te_y_arr[0] - 10.0)]
            te_pad_pts.extend(list(zip(te_x_arr, te_y_arr)))
            te_pad_pts.append((te_support_end_x, te_y_arr[-1] - 10.0))
            te_pad_pts.append((te_support_start_x, te_y_arr[0] - 10.0)) # Close
            te_pad = Polygon(te_pad_pts).buffer(0)
            frame = frame.union(te_pad)

        # Then subtract the whole wing profile so nothing enters the wing
        # EXCEPT we protect the spar areas so the pillars can reach the spars!
        wing_poly = Polygon(np.column_stack((np.concatenate((u_x, l_x)), np.concatenate((u_y, l_y)))))
        wing_cut_tool = wing_poly.buffer(1.0).buffer(0)
        
        # Protect spar regions
        protected_boxes = []
        if d_m > 0: protected_boxes.append(box(c_m[0] - d_m/2.0 - 5.0, -1000, c_m[0] + d_m/2.0 + 5.0, 1000))
        if d_f > 0: protected_boxes.append(box(c_f[0] - d_f/2.0 - 5.0, -1000, c_f[0] + d_f/2.0 + 5.0, 1000))
        if d_r > 0: protected_boxes.append(box(c_r[0] - d_r/2.0 - 5.0, -1000, c_r[0] + d_r/2.0 + 5.0, 1000))
        
        if protected_boxes:
            wing_cut_tool = wing_cut_tool.difference(unary_union(protected_boxes))
            
        frame = frame.difference(wing_cut_tool)
        

            
        # Cut spar holes (U shaped)
        if d_f > 0:
            f_hole = Point(c_f).buffer(d_f/2.0)
            f_cut = box(c_f[0] - d_f, c_f[1], c_f[0] + d_f, c_f[1] + d_f)
            frame = frame.difference(f_hole.union(f_cut))
            
        if d_m > 0:
            m_hole = Point(c_m).buffer(d_m/2.0)
            m_cut = box(c_m[0] - d_m, c_m[1], c_m[0] + d_m, c_m[1] + d_m)
            frame = frame.difference(m_hole.union(m_cut))
            
        if d_r > 0:
            r_hole = Point(c_r).buffer(d_r/2.0)
            r_cut = box(c_r[0] - d_r, c_r[1], c_r[0] + d_r, c_r[1] + d_r)
            frame = frame.difference(r_hole.union(r_cut))
            
        # Slots on the base plate
        slot_width = p.get('jig_slot_width', 3.0)
        slot_depth = p.get('jig_slot_depth', 10.0)
        
        s1 = box(slot1_x - slot_width/2.0, base_y - 1.0, slot1_x + slot_width/2.0, base_y + slot_depth)
        s2 = box(slot2_x - slot_width/2.0, base_y - 1.0, slot2_x + slot_width/2.0, base_y + slot_depth)
        frame = frame.difference(s1.union(s2))
        
        # Extract polygon coordinates
        if getattr(frame, 'geom_type', '') == 'Polygon':
            return list(frame.exterior.coords)
        elif getattr(frame, 'geom_type', '') == 'MultiPolygon':
            largest = max(frame.geoms, key=lambda a: a.area)
            return list(largest.exterior.coords)
        
        return []