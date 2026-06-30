import sys
sys.path.append('.')
from core.export_3d import Wing3DBuilder, Wing3DExporter
from core.engine import RibGeneratorEngine
import json

engine = RibGeneratorEngine()
with open('26_3rd.json') as f:
    raw_p = json.load(f)

import ui.batch_mode
import tkinter as tk
root = tk.Tk()
batch = ui.batch_mode.RibGeneratorGUI_Batch(root)
batch.load_settings_from_json('26_3rd.json')
p = batch._get_builder_params()
p['tabs_active'] = False
p['export_ribs'] = True
p['export_carbon_ribs'] = True
p['export_connectors'] = True
p['export_te'] = False # Disable TE to avoid blender difference

builder = Wing3DBuilder(engine, p)
scene_geoms, _ = builder.build_geometry()

print("Available keys in scene_geoms:", scene_geoms.keys())
if 'Ribs' in scene_geoms:
    rib_mesh = scene_geoms['Ribs']
    print(f"Ribs mesh has {len(rib_mesh.vertices)} vertices, {len(rib_mesh.faces)} faces")
else:
    print("Ribs is missing!")

