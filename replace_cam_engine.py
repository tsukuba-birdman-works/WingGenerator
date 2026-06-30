import re

with open("core/cam_engine.py", "r") as f:
    code = f.read()

# 1. Update get_z_at_point to use tab_angle_deg
replacement_z = """    def get_z_at_point(self, x: float, y: float, tab_centers: List[Tuple[float, float]], 
                       tab_width: float, cut_z: float, tab_z: float,
                       is_outer: bool, spar_x_coords: List[float], spar_y_shifted: float,
                       tab_angle_deg: float = 45.0) -> float:
        \"\"\"Return the target Z height. If the tool is within the tab zone, lift towards tab_z using tab_angle_deg.\"\"\"
        target_z = cut_z
        
        for tx, ty in tab_centers:
            # For outer path, tab_centers contains the explicitly generated outer tabs
            # For inner path, tab_centers contains the truss hole tabs
            dist = np.hypot(x - tx, y - ty)
            w_half = tab_width / 2.0
            
            if dist <= w_half:
                # Flat bottom of the tab
                candidate_z = tab_z
                target_z = max(target_z, candidate_z)
            else:
                # Ramp up
                import math
                angle_rad = math.radians(tab_angle_deg)
                if angle_rad <= 0:
                    angle_rad = math.radians(90.0) # Vertical if 0
                
                # Z increases as dist increases beyond w_half
                ramp_distance = dist - w_half
                ramp_z = tab_z - (ramp_distance * math.tan(angle_rad))
                
                # If ramp_z is deeper than cut_z, we just cut at cut_z
                candidate_z = max(cut_z, ramp_z)
                target_z = max(target_z, candidate_z)
                
        return min(target_z, tab_z) # Cap at tab_z"""

code = re.sub(r"    def get_z_at_point.*?return cut_z", replacement_z, code, flags=re.DOTALL)


# 2. Parse new parameters in generate_gcode
parse_replacement = """        tab_width = float(params.get('truss_tab_width', '4.0')) # default to truss tab width
        outer_tab_w = float(params.get('outer_tab_width', '6.0'))
        outer_tab_interval = float(params.get('outer_tab_interval', '100.0'))
        tab_angle_deg = float(params.get('tab_angle_deg', '45.0'))
        tabs_active = bool(params.get('tabs_active', True))"""
code = re.sub(r"        tab_width = float\(params\.get\('truss_tab_width', '4\.0'\)\) # default to truss tab width\n        spar_tab_w = float\(params\.get\('spar_tab_width', '6\.0'\)\)\n        tabs_active = bool\(params\.get\('tabs_active', True\)\)", parse_replacement, code)


# 3. Create Exclusion Zones
# Before the toolpath loop:
exclusion_code = """
        # --- Prepare Exclusion Zones for Outer Tabs ---
        exclusion_zones_x = []
        # 1. LE / TE (First and last 30mm of rib)
        rib_min_x, rib_max_x = 0.0, 0.0
        if poly_rib and poly_rib.is_valid:
            bounds = poly_rib.bounds
            rib_min_x, rib_max_x = bounds[0], bounds[2]
            exclusion_zones_x.append((rib_min_x - 1000.0, rib_min_x + 30.0))
            exclusion_zones_x.append((rib_max_x - 30.0, rib_max_x + 1000.0))
            
        # 2. Stringers (±10mm)
        if hasattr(rib_res, 'stringer_pts_list') and rib_res.stringer_pts_list:
            for st_pts in rib_res.stringer_pts_list:
                s_pts = [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in st_pts]
                if s_pts:
                    min_sx = min(p[0] for p in s_pts)
                    max_sx = max(p[0] for p in s_pts)
                    exclusion_zones_x.append((min_sx - 10.0, max_sx + 10.0))
                    
        # 3. Plank Steps (±10mm)
        if hasattr(rib_res, 'plank_poly_rot') and rib_res.plank_poly_rot and rib_res.plank_poly_rot.is_valid:
            p_bounds = rib_res.plank_poly_rot.bounds
            p_min_x, p_max_x = p_bounds[0] - origin_pt[0], p_bounds[2] - origin_pt[0]
            # The steps are at p_min_x and p_max_x
            exclusion_zones_x.append((p_min_x - 10.0, p_min_x + 10.0))
            exclusion_zones_x.append((p_max_x - 10.0, p_max_x + 10.0))

        # Inner toolpaths first, then outer toolpath"""
code = code.replace("        # Inner toolpaths first, then outer toolpath", exclusion_code)

# 4. Generate outer tab centers inside the toolpath loop
outer_tab_logic = """            # Resample the path to 1mm resolution
            dense_path = self.resample_path(path, spacing=1.0)
            if not dense_path:
                continue
                
            # If the path is closed, close it exactly
            if np.allclose(dense_path[0], dense_path[-1]):
                dense_path[-1] = dense_path[0]
                
            # --- Outer Tab Generation ---
            current_tab_centers = shifted_tab_centers
            if is_outer and tabs_active and outer_tab_interval > 0:
                current_tab_centers = []
                path_len = len(dense_path)
                num_tabs = int(path_len / outer_tab_interval)
                if num_tabs > 0:
                    step = path_len // num_tabs
                    for t_idx in range(step // 2, path_len, step):
                        # Find a valid index avoiding exclusions
                        valid_pt = None
                        search_range = step // 2
                        for offset in range(search_range):
                            for sign in (1, -1):
                                test_idx = t_idx + sign * offset
                                if 0 <= test_idx < path_len:
                                    pt_x = dense_path[test_idx][0]
                                    in_exclusion = False
                                    for ex_min, ex_max in exclusion_zones_x:
                                        if ex_min <= pt_x <= ex_max:
                                            in_exclusion = True
                                            break
                                    if not in_exclusion:
                                        valid_pt = dense_path[test_idx]
                                        break
                            if valid_pt:
                                break
                        if valid_pt:
                            current_tab_centers.append((valid_pt[0], valid_pt[1]))
            # --------------------------

            start_pt = dense_path[0]"""
code = code.replace("""            # Resample the path to 1mm resolution
            dense_path = self.resample_path(path, spacing=1.0)
            if not dense_path:
                continue
                
            # If the path is closed, close it exactly
            if np.allclose(dense_path[0], dense_path[-1]):
                dense_path[-1] = dense_path[0]

            start_pt = dense_path[0]""", outer_tab_logic)

# 5. Fix get_target_z call
call_z_replace = """            cur_tab_w = outer_tab_w if is_outer else tab_width
            
            def get_target_z(x, y):
                if specific_z is not None:
                    return specific_z
                if has_tabs and tabs_active:
                    return self.get_z_at_point(x, y, current_tab_centers, cur_tab_w, cut_z, tab_z, is_outer, spar_x_coords, 0.0, tab_angle_deg)
                return cut_z"""
code = re.sub(r"            cur_tab_w = spar_tab_w if is_outer else tab_width\n\s+def get_target_z\(x, y\):\n\s+if specific_z is not None:\n\s+return specific_z\n\s+if has_tabs and tabs_active:\n\s+return self\.get_z_at_point\(x, y, shifted_tab_centers, cur_tab_w, cut_z, tab_z, is_outer, spar_x_coords, 0\.0\)\n\s+return cut_z", call_z_replace, code)

with open("core/cam_engine.py", "w") as f:
    f.write(code)
print("cam_engine patched successfully.")
