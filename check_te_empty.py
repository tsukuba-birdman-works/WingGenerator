import sys
import json
sys.path.append('.')
from core.engine import RibGeneratorEngine

try:
    with open('26_htail.json', 'r') as f:
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
except:
    sys.exit(1)

import glob
dats = glob.glob('Airfoils/*.dat')
if dats:
    params['file1_path'] = dats[0]
    params['file2_path'] = dats[0]

engine = RibGeneratorEngine()
params['wing_span'] = params.get('wing_span', 1000)
params['chord_root'] = params.get('chord_root', 200)
engine.update(params) # this calculates y_positions
p = engine.p

print("y_positions:", p.get('y_positions'))
print("te_cut:", p.get('te_cut'))
print("te_cut_tip:", p.get('te_cut_tip'))

for i, y_local in enumerate(p['y_positions']):
    res = engine.generate_rib_at_y(p, y_local, i, p['rib_thick'], False)
    print(f"Rib {i} at y={y_local}: len(res[14]) = {len(res[14]) if len(res) > 14 else 'N/A'}")
