import math
import numpy as np
from core.cam_engine import SpindleCAMEngine

cam = SpindleCAMEngine()
# Simulate tab_thickness = 9.0, mat_thick = 10.0 => tab_z = -1.0, cut_z = -10.5
tab_z = -1.0
cut_z = -10.5
tab_width = 6.0
tab_angle_deg = 45.0
is_outer = True
spar_x_coords = []
spar_y_shifted = 0.0

tab_centers = [(0.0, 0.0)]

print(f"Tab Z: {tab_z}, Cut Z: {cut_z}, Tab Width: {tab_width}, Angle: {tab_angle_deg}")

for x in range(0, 11):
    z = cam.get_z_at_point(x, 0.0, tab_centers, tab_width, cut_z, tab_z, is_outer, spar_x_coords, spar_y_shifted, tab_angle_deg)
    print(f"x={x}: z={z:.3f}")

