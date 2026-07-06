import sys

with open("core/cam_engine.py", "r") as f:
    code = f.read()

# Replace hardcoded exclusion limits with params.get
bad_exclusions = """        # Exclusion Zones Configuration
        exclusion_zones_x = []
        
        # 1. Leading/Trailing Edge (±30mm from bounds)
        rib_min_x = min(p[0] for p in outer_path)
        rib_max_x = max(p[0] for p in outer_path)
        exclusion_zones_x.append((rib_min_x, rib_min_x + 30.0))
        exclusion_zones_x.append((rib_max_x - 30.0, rib_max_x))
        
        # 2. Stringer Holes (±10mm from center)
        if hasattr(rib_res, 'stringer_pts_list') and rib_res.stringer_pts_list:
            for s_pts in rib_res.stringer_pts_list:
                s_min_x = min(p[0] for p in s_pts) - origin_pt[0]
                s_max_x = max(p[0] for p in s_pts) - origin_pt[0]
                # Center is roughly (s_min_x + s_max_x) / 2
                s_cx = (s_min_x + s_max_x) / 2.0
                exclusion_zones_x.append((s_cx - 10.0, s_cx + 10.0))
                
        # 3. Plank Steps (±10mm)
        if hasattr(rib_res, 'plank_poly_rot'):
            p_arr = rib_res.plank_poly_rot
            if len(p_arr) > 0:
                p_min_x = min(p[0] for p in p_arr) - origin_pt[0]
                p_max_x = max(p[0] for p in p_arr) - origin_pt[0]
                exclusion_zones_x.append((p_min_x - 10.0, p_min_x + 10.0))
                exclusion_zones_x.append((p_max_x - 10.0, p_max_x + 10.0))"""

good_exclusions = """        # Exclusion Zones Configuration
        exclusion_zones_x = []
        excl_le_te = float(params.get('tab_exclusion_le_te', '30.0'))
        excl_str = float(params.get('tab_exclusion_stringer', '10.0'))
        
        # 1. Leading/Trailing Edge (± excl_le_te mm from bounds)
        rib_min_x = min(p[0] for p in outer_path)
        rib_max_x = max(p[0] for p in outer_path)
        exclusion_zones_x.append((rib_min_x, rib_min_x + excl_le_te))
        exclusion_zones_x.append((rib_max_x - excl_le_te, rib_max_x))
        
        # 2. Stringer Holes (± excl_str mm from center)
        if hasattr(rib_res, 'stringer_pts_list') and rib_res.stringer_pts_list:
            for s_pts in rib_res.stringer_pts_list:
                s_min_x = min(p[0] for p in s_pts) - origin_pt[0]
                s_max_x = max(p[0] for p in s_pts) - origin_pt[0]
                # Center is roughly (s_min_x + s_max_x) / 2
                s_cx = (s_min_x + s_max_x) / 2.0
                exclusion_zones_x.append((s_cx - excl_str, s_cx + excl_str))
                
        # 3. Plank Steps (± excl_str mm)
        if hasattr(rib_res, 'plank_poly_rot'):
            p_arr = rib_res.plank_poly_rot
            if len(p_arr) > 0:
                p_min_x = min(p[0] for p in p_arr) - origin_pt[0]
                p_max_x = max(p[0] for p in p_arr) - origin_pt[0]
                exclusion_zones_x.append((p_min_x - excl_str, p_min_x + excl_str))
                exclusion_zones_x.append((p_max_x - excl_str, p_max_x + excl_str))"""

code = code.replace(bad_exclusions, good_exclusions)

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Updated cam_engine.py exclusions")
