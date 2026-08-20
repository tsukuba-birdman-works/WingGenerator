import sys, os
sys.path.append(os.path.abspath('.'))
from core.fea_engine import RibFEAEngine
from shapely.geometry import Polygon

engine = RibFEAEngine(work_dir="scratch")
engine.load_lift_csv("test_lift_dist.csv")

outer = [(0, 0), (100, 0), (100, 20), (0, 20)]
hole = [(40, 5), (60, 5), (60, 15), (40, 15)]
poly = Polygon(outer, [hole])

inp_path = engine.generate_fea_model(poly, spar_pos=(50, 10), chord=100.0, material_props={'E': 15.0, 'nu': 0.3}, thickness=5.0)
print(f"Generated {inp_path}")

import subprocess
res = subprocess.run(["ccx", "rib_fea"], cwd="scratch", capture_output=True, text=True)
if res.returncode == 0:
    print("CalculiX ran successfully!")
    if os.path.exists("scratch/rib_fea.dat"):
        print(".dat file created.")
else:
    print("CalculiX failed!")
    print(res.stderr)
