import sys
import json
import numpy as np
sys.path.append('.')
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter

with open('Ribgenerator.json', 'r') as f:
    j = json.load(f)

# Extract config
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

print("Y positions:", params.get('y_positions'))

engine = RibGeneratorEngine()
exporter = Wing3DExporter(engine, params)
res = exporter._collect_geometry_data()
scene_rib_data = res[0]
print("scene_rib_data count:", len(scene_rib_data))
for i, d in enumerate(scene_rib_data):
    print(f"Rib {i}: y={d[0]}, t={d[1]}, mat={d[4]}")
