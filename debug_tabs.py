import sys
import os
import math
sys.path.append(os.getcwd())

from core.engine import RibGeneratorEngine
from core.cam_engine import SpindleCAMEngine
from ui.ui_builder import ProjectManager

pm = ProjectManager()
pm.load_project("26_0th.json")

# Force user's extreme settings
pm.obj.params['tab_thickness'] = 9.0
pm.obj.params['outer_tab_width'] = 10.0
pm.obj.params['truss_tab_width'] = 10.0
pm.obj.params['outer_tab_interval'] = 100.0
pm.obj.params['tab_angle_deg'] = 80.0
pm.obj.params['tabs_active'] = True
pm.obj.params['cam_mat_thick'] = 10.0
pm.obj.params['cam_extra_depth'] = 0.5

eng = RibGeneratorEngine()
cam = SpindleCAMEngine()

rb = pm.obj.rib_batches[0]
p = eng.parse_params(pm.obj.params, rb, 0)
res = eng.generate_rib("data/naca4415.dat", "data/naca4415.dat", p, 0.0)

if res:
    gcode, warn = cam.generate_gcode(res, pm.obj.params)
    lines = gcode.splitlines()
    
    max_z_outer = -999.0
    in_outer = False
    
    for l in lines:
        if "Rib Outer Contour" in l:
            in_outer = True
        if in_outer and "Z" in l:
            parts = l.split()
            for part in parts:
                if part.startswith("Z"):
                    try:
                        z_val = float(part[1:])
                        if z_val > max_z_outer and z_val <= 0:
                            max_z_outer = z_val
                    except:
                        pass
    print(f"Max Z in outer contour (excluding G0 safe heights > 0): {max_z_outer}")
    
    # Let's also print the Z values around the first tab center!
    outer_tab_centers = None
    # Actually, we can just print the highest Z values found in the gcode
    z_vals = []
    in_outer = False
    for l in lines:
        if "Rib Outer Contour" in l:
            in_outer = True
        if in_outer and l.startswith("G1"):
            if "Z" in l:
                for part in l.split():
                    if part.startswith("Z"):
                        z = float(part[1:])
                        if z <= 0.0:
                            z_vals.append(z)
    
    z_vals.sort(reverse=True)
    print("Top 10 highest Z values in outer cut:", z_vals[:10])
