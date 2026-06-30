import sys
import os
sys.path.append(os.getcwd())

from core.engine import RibGeneratorEngine
from core.cam_engine import SpindleCAMEngine
from core.config import ProjectObject

obj = ProjectObject.load("26_0th.json")

# Force user's extreme settings
obj.params['tab_thickness'] = 9.0
obj.params['outer_tab_width'] = 10.0
obj.params['truss_tab_width'] = 10.0
obj.params['outer_tab_interval'] = 100.0
obj.params['tab_angle_deg'] = 80.0
obj.params['tabs_active'] = True
obj.params['cam_mat_thick'] = 10.0
obj.params['cam_extra_depth'] = 0.5

eng = RibGeneratorEngine()
cam = SpindleCAMEngine()

rb = obj.rib_batches[0]
p = eng.parse_params(obj.params, rb, 0)
res = eng.generate_rib("data/naca4415.dat", "data/naca4415.dat", p, 0.0)

if res:
    gcode, warn = cam.generate_gcode(res, obj.params)
    lines = gcode.splitlines()
    
    z_vals = []
    in_outer = False
    for l in lines:
        if "Rib Outer Contour" in l:
            in_outer = True
        if in_outer and l.startswith("G1") and "Z" in l:
            for part in l.split():
                if part.startswith("Z"):
                    z = float(part[1:])
                    if z <= 0.0:
                        z_vals.append(z)
    
    z_vals.sort(reverse=True)
    print("Top 10 highest Z values in outer cut:", z_vals[:10])
