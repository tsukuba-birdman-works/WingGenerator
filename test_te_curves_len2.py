import sys
import os
sys.path.append(os.getcwd())
import json
from core.export_3d import Wing3DExporter
from core.engine import RibGeneratorEngine

try:
    with open('Ribgenerator.json', 'r') as f:
        params = json.load(f)
except:
    print("Could not load params")
    sys.exit(1)

class MockApp:
    def __init__(self):
        self.p = params
        self.engine = RibGeneratorEngine()
    def _to_rel(self, pts, c_m):
        return [[p[0]-c_m[0], p[1]-c_m[1], p[2]-c_m[2]] for p in pts]

app = MockApp()
exporter = Wing3DExporter(app)

scene_rib_data, other_meshes, part_colors, _rib_orig, _te_span = exporter._collect_geometry_data()

import numpy as np
for name, mesh in other_meshes.items():
    if name == 'TE_Skin':
        print(f"TE_Skin faces: {len(mesh.faces)}")
