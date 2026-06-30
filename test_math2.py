import math
import numpy as np

tab_width = 10.0
tab_z = -1.0 # 9mm thickness with 10mm material
cut_z = -10.5
tab_angle_deg = 80.0
angle_rad = math.radians(tab_angle_deg)
w_half = tab_width / 2.0

for dist in [6.0, 5.1, 5.0, 4.0, 3.0, 0.0]:
    if dist <= w_half:
        candidate_z = tab_z
        target_z = max(cut_z, candidate_z)
        print(f"Dist: {dist}, target_z: {target_z:.3f} (FLAT TOP)")
    else:
        ramp_distance = dist - w_half
        ramp_z = tab_z - (ramp_distance * math.tan(angle_rad))
        candidate_z = max(cut_z, ramp_z)
        target_z = max(cut_z, candidate_z)
        print(f"Dist: {dist}, ramp_z: {ramp_z:.3f}, target_z: {target_z:.3f} (SLOPE)")
