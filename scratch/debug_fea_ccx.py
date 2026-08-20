import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine, RibParameters
from core.fea_engine import RibFEAEngine
from shapely.geometry import Polygon
import numpy as np

engine = RibGeneratorEngine()
params = RibParameters(
    chord=200, spar_pct=0.3, spar_dia=10, 
    truss_front_margin=5, truss_rear_margin=5, truss_holes_count=5,
    st_upper=[(0.2, 5, 5)], st_lower=[(0.2, 5, 5)], 
    washout=0, blend_enabled=False
)

res = engine.generate_rib_at_y(params, 0.0)

holes = []
if res.hole_m is not None and len(res.hole_m)>2: holes.append(res.hole_m)
if res.hole_f is not None and len(res.hole_f)>2: holes.append(res.hole_f)
if res.hole_r is not None and len(res.hole_r)>2: holes.append(res.hole_r)
if res.final_truss_holes is not None:
    for h in res.final_truss_holes:
        if len(h) > 2: holes.append(h)

poly = Polygon(res.final_rib_mod, holes).buffer(0)

fea = RibFEAEngine(work_dir="scratch")
fea.load_lift_csv("lift_distribution_sample.csv")

stringers = params.st_upper + params.st_lower
stringer_x = [st[0]*params.chord for st in stringers]

inp_path = fea.generate_fea_model(poly, (params.chord*params.spar_pct, 0), params.chord, {'E':15,'nu':0.3}, 5.0, stringer_x=stringer_x)
print(f"Generated {inp_path}")

import subprocess
import shutil

job = os.path.splitext(os.path.basename(inp_path))[0]
ccx_res = subprocess.run(["ccx", job], cwd="scratch", capture_output=True, text=True)

print("Return Code:", ccx_res.returncode)
print("STDOUT (last 20 lines):")
print("\n".join(ccx_res.stdout.splitlines()[-20:]))
print("STDERR:")
print(ccx_res.stderr)
