import sys
import json
import os
import glob
import numpy as np
import trimesh

sys.path.append('.')
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder

jsons = glob.glob('*.json')
jsons.sort(key=os.path.getmtime, reverse=True)
latest_json = jsons[0]

with open(latest_json, 'r') as f:
    j = json.load(f)
params = {}
for k, v in j.items():
    if isinstance(v, dict):
        for kk, vv in v.items():
            if isinstance(vv, dict):
                params.update(vv)
            else:
                params[kk] = vv
    else:
        params[k] = v

dats = glob.glob('Airfoils/*.dat')
if dats:
    params['file1_path'] = dats[0]
    params['file2_path'] = dats[0]

# Force TE settings to ensure boolean intersection
params['te_cut'] = 30
params['plank_act'] = False

engine = RibGeneratorEngine()
params['y_positions'] = [0, 500, 1000]
engine.p = params

builder = Wing3DBuilder(engine, params)
res = builder.build_and_export('scratch/test_te_native.glb')

print("Mesh exported to scratch/test_te_native.glb")
