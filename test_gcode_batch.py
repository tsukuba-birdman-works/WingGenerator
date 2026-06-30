import sys
import os
import json
sys.path.append(os.getcwd())

from core.engine import RibGeneratorEngine
from core.cam_engine import SpindleCAMEngine
from ui.project_manager import ProjectManager

pm = ProjectManager()
pm.load_project("26_0th.json")

# Add outer tab params to project params
pm.obj.params['outer_tab_width'] = 6.0
pm.obj.params['outer_tab_interval'] = 50.0
pm.obj.params['tab_angle_deg'] = 45.0
pm.obj.params['tabs_active'] = True

eng = RibGeneratorEngine()
cam = SpindleCAMEngine()

# Find the first valid rib setup
for rb in pm.obj.rib_batches:
    p = eng.parse_params(pm.obj.params, rb, 0)
    res = eng.generate_rib("data/naca4415.dat", "data/naca4415.dat", p, 0.0)
    if res:
        gcode, warn = cam.generate_gcode(res, pm.obj.params)
        with open("test_batch_out.gcode", "w") as f:
            f.write(gcode)
        
        tab_z_count = 0
        in_outer = False
        for l in gcode.splitlines():
            if "Rib Outer Contour" in l:
                in_outer = True
            if in_outer and "Z" in l:
                parts = l.split()
                for part in parts:
                    if part.startswith("Z"):
                        try:
                            z_val = float(part[1:])
                            if z_val > -10.0:  # Material thick is 10, cut is -10.5. Tab is higher.
                                tab_z_count += 1
                        except:
                            pass
        print(f"Number of Z-lifts in outer contour: {tab_z_count}")
        break
