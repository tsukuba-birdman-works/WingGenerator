import sys, os, json
sys.path.append('.')
from ui.batch_mode import RibGeneratorGUI_Batch
from core.export_3d import Wing3DBuilder
import tkinter as tk

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
with open('preset/test.json', 'r') as f:
    app.pm.obj.data = json.load(f)

# Force the file paths and some vars that the batch ui expects from TK Variables
app.file1_path.set('airfoil/dae51.dat')
app.file2_path.set('airfoil/dae51.dat')
app.wing_span.set('1000')
app.root_chord.set('200')
app.taper_ratio.set('0.5')
app.sweep_angle.set('20')
app.num_ribs.set('15')
app.calculate_y_positions()

params = app._get_builder_params()
params['tabs_active'] = False
params['export_te'] = True
params['export_ribs'] = True
params['export_carbon_ribs'] = True
params['carbon_rib_configs'] = [{'act': True, 'idx': 14, 'loc': 'tip', 'pos': 'outer', 'te': True}]

builder = Wing3DBuilder(app.engine, params)
builder.build_and_export("scratch/test_tip_issue.glb")

print("Done")
root.destroy()
