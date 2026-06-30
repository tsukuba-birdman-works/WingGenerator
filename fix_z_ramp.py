with open("core/cam_engine.py", "r") as f:
    code = f.read()

bad_logic = """        for tx, ty in tab_centers:
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

good_logic = """        for tx, ty in tab_centers:
            # For outer path, tab_centers contains the explicitly generated outer tabs
            # For inner path, tab_centers contains the truss hole tabs
            dist = np.hypot(x - tx, y - ty)
            w_half = tab_width / 2.0
            
            if dist < w_half:
                import math
                angle_rad = math.radians(tab_angle_deg)
                if angle_rad <= 0:
                    angle_rad = math.radians(90.0)
                
                # Ramp starts from the bottom (cut_z) at dist == w_half
                # and goes UP as dist approaches 0.
                ramp_distance = w_half - dist
                ramp_z = cut_z + (ramp_distance * math.tan(angle_rad))
                
                # Cap the height at tab_z (flat top)
                candidate_z = min(ramp_z, tab_z)
                target_z = max(target_z, candidate_z)
                
        return target_z"""

code = code.replace(bad_logic, good_logic)

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Z ramp fixed!")
