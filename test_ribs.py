import sys
sys.path.append('.')
from core.export_3d import Wing3DBuilder, Wing3DExporter
from core.engine import RibGeneratorEngine
import json
import trimesh

engine = RibGeneratorEngine()
with open('26_3rd.json') as f:
    raw_p = json.load(f)

# Mock _get_builder_params logic
p = raw_p.copy()
# set y_positions to dummy
p['y_positions'] = [0, 50, 100, 150, 200]
p['truss_angles_dict'] = {}
p['stringers_data'] = []
p['tabs_active'] = False
p['export_ribs'] = True
p['export_carbon_ribs'] = True
p['export_connectors'] = False
p['export_te'] = False
p['connectors'] = []
p['carbon_rib_configs'] = [
    {'loc': 'root', 'pos': 'inner', 'idx': 0, 'act': True, 'te': False},
    {'loc': 'root', 'pos': 'outer', 'idx': 0, 'act': False, 'te': False},
    {'loc': 'tip', 'pos': 'inner', 'idx': len(p['y_positions'])-1, 'act': False, 'te': False},
    {'loc': 'tip', 'pos': 'outer', 'idx': len(p['y_positions'])-1, 'act': False, 'te': False},
]

builder = Wing3DBuilder(engine, p)
scene_geoms, _ = builder.build_geometry()

print("Available keys in scene_geoms:", scene_geoms.keys())
if 'Ribs' in scene_geoms:
    rib_mesh = scene_geoms['Ribs']
    print(f"Ribs mesh has {len(rib_mesh.vertices)} vertices, {len(rib_mesh.faces)} faces")
else:
    print("Ribs is missing!")
