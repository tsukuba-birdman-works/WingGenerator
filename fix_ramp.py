import re

with open("core/cam_engine.py", "r") as f:
    code = f.read()

replacement = """    def get_z_at_point(self, x: float, y: float, tab_centers: List[Tuple[float, float]], 
                       tab_width: float, cut_z: float, tab_z: float,
                       is_outer: bool, spar_x_coords: List[float], spar_y_shifted: float,
                       tab_angle_deg: float = 45.0) -> float:
        \"\"\"Return the target Z height. If the tool is within the tab zone, lift towards tab_z using tab_angle_deg.\"\"\"
        target_z = cut_z
        
        for tx, ty in tab_centers:
            dist = np.hypot(x - tx, y - ty)
            w_half = tab_width / 2.0
            
            if dist < w_half:
                import math
                angle_rad = math.radians(tab_angle_deg)
                if angle_rad <= 0:
                    angle_rad = math.radians(90.0)
                    
                # User requested BASE WIDTH to be tab_width.
                # So at dist == w_half, z == cut_z. As dist -> 0, z goes UP.
                ramp_z = cut_z + (w_half - dist) * math.tan(angle_rad)
                
                # The Z cannot go higher than tab_z (the flat top limit)
                candidate_z = min(tab_z, ramp_z)
                target_z = max(target_z, candidate_z)
                
        return target_z"""

code = re.sub(r"    def get_z_at_point\(self, x: float, y: float, tab_centers: List\[Tuple\[float, float\]\],.*?(?=\n\s+def generate_gcode)", replacement, code, flags=re.DOTALL)

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Fixed Z ramp logic!")
