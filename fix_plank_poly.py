with open("core/cam_engine.py", "r") as f:
    code = f.read()

bad_code = """        # 3. Plank Steps (±10mm)
        if hasattr(rib_res, 'plank_poly_rot') and rib_res.plank_poly_rot and rib_res.plank_poly_rot.is_valid:
            p_bounds = rib_res.plank_poly_rot.bounds
            p_min_x, p_max_x = p_bounds[0] - origin_pt[0], p_bounds[2] - origin_pt[0]
            # The steps are at p_min_x and p_max_x
            exclusion_zones_x.append((p_min_x - 10.0, p_min_x + 10.0))
            exclusion_zones_x.append((p_max_x - 10.0, p_max_x + 10.0))"""

good_code = """        # 3. Plank Steps (±10mm)
        if hasattr(rib_res, 'plank_poly_rot'):
            p_arr = rib_res.plank_poly_rot
            if len(p_arr) > 0:
                p_min_x = min(p[0] for p in p_arr) - origin_pt[0]
                p_max_x = max(p[0] for p in p_arr) - origin_pt[0]
                exclusion_zones_x.append((p_min_x - 10.0, p_min_x + 10.0))
                exclusion_zones_x.append((p_max_x - 10.0, p_max_x + 10.0))"""

code = code.replace(bad_code, good_code)

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Fixed plank_poly_rot check")
