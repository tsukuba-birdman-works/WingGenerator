import sys
import json
import os
import glob

jsons = glob.glob('*.json')
jsons.sort(key=os.path.getmtime, reverse=True)
latest_json = jsons[0]

print("Using config:", latest_json)
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

sys.path.append('.')
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder

engine = RibGeneratorEngine()
# calculate derived params
params['wing_span'] = params.get('wing_span', 1000)
params['chord_root'] = params.get('chord_root', 200)
engine.update(params) # this calculates y_positions
# update params from engine
params.update(engine.p)

builder = Wing3DBuilder(engine, params)
builder.build_and_export('test_final_export.glb')
print("Exported test_final_export.glb")
