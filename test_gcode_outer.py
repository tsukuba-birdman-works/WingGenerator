import sys
import os
from core.engine import RibGeneratorEngine, RibParameters
from core.cam_engine import SpindleCAMEngine

sys.path.append(os.getcwd())

engine = RibGeneratorEngine()
p = RibParameters()
p.wing_span = 1000.0
p.fast_mode = True
p.tabs_active = True

res = engine.generate_rib("data/naca4415.dat", "data/naca4415.dat", p, 500.0)

cam = SpindleCAMEngine()
params = {
    'cam_tool_dia': 2.0,
    'cam_mat_thick': 10.0,
    'cam_safe_z': 5.0,
    'truss_tab_width': 4.0,
    'outer_tab_width': 6.0,
    'outer_tab_interval': 100.0,
    'tab_thickness': 3.0,
    'tab_angle_deg': 45.0,
    'tabs_active': True,
    'spar_hole_dia': 10.0,
    'front_spar_dia': 6.0,
    'rear_spar_dia': 6.0
}

gcode, warnings = cam.generate_gcode(res, params)
with open("test_out.gcode", "w") as f:
    f.write(gcode)

print("Warnings:", warnings)
print("Outer contour block lines:")
lines = gcode.splitlines()
in_outer = False
tab_z_count = 0
for l in lines:
    if "Rib Outer Contour" in l:
        in_outer = True
    if in_outer and "Z-" in l:
        z_val = float(l.split("Z")[1].split()[0])
        if z_val > -10.0:  # Higher than cut depth
            tab_z_count += 1

print(f"Number of Z-lifts in outer contour: {tab_z_count}")
