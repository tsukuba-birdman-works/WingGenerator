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
params['wing_span'] = params.get('wing_span', 1000)
params['chord_root'] = params.get('chord_root', 200)

from ui.data_manager import DataManager
class DummyUI:
    def __init__(self):
        self.p = params
ui = DummyUI()
# Call calculate_y_positions
# Wait, let's just manually set y_positions
def get_y_pos(p):
    span = p['wing_span']
    y_pos = []
    if p['y_spacing_type'] == 'Equal':
        n = int(p['num_ribs'])
        if n < 2: n = 2
        for i in range(n):
            y_pos.append(i * span / (n - 1))
    return y_pos
params['y_positions'] = get_y_pos(params)
engine.p = params

builder = Wing3DBuilder(engine, params)
builder.build_and_export('test_final_native.glb')
print("Exported test_final_native.glb")
