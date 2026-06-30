import re

with open("core/cam_engine.py", "r") as f:
    code = f.read()

replacement_z = """    def get_z_at_point(self, x: float, y: float, tab_centers: List[Tuple[float, float]],
                       tab_width: float, cut_z: float, tab_z: float,
                       is_outer: bool, spar_x_coords: List[float], spar_y_shifted: float,
                       tab_angle_deg: float = 45.0) -> float:
        \"\"\"Return the target Z height. If the tool is within the tab zone, lift towards tab_z using tab_angle_deg.\"\"\"
        target_z = cut_z
        
        for tx, ty in tab_centers:
            dist = (x - tx)**2 + (y - ty)**2
            dist = dist ** 0.5
            w_half = tab_width / 2.0
            
            if dist <= w_half:
                # Flat top of the tab (the uncut material left)
                candidate_z = tab_z
                target_z = max(target_z, candidate_z)
            else:
                # Ramp down towards cut_z
                import math
                angle_rad = math.radians(tab_angle_deg)
                if angle_rad <= 0:
                    angle_rad = math.radians(90.0)
                    
                # Z decreases (goes deeper) as dist increases beyond w_half
                ramp_distance = dist - w_half
                ramp_z = tab_z - (ramp_distance * math.tan(angle_rad))
                
                # The Z cannot go deeper than cut_z
                candidate_z = max(cut_z, ramp_z)
                target_z = max(target_z, candidate_z)
                
        return min(target_z, tab_z) # Cap at tab_z (safety)"""

code = re.sub(r"    def get_z_at_point.*?return target_z", replacement_z, code, flags=re.DOTALL)

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Fixed get_z_at_point")
