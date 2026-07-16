import sys, os
import numpy as np
sys.path.append('.')
from core.export_3d import Wing3DExporter
from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
app.p['chord'] = 200
app.p['taper_ratio'] = 0.3
app.p['sweep_angle'] = 15
app.p['wing_span'] = 1000
app.p['num_ribs'] = 5
app.p['te_cut'] = 20
app.p['export_te'] = True
app.p['export_carbon_ribs'] = True

params_list = app.get_rib_parameters(fast_mode=False)
exporter = Wing3DExporter(app.p)
exporter.generate_meshes(params_list, "scratch/test_tip_out.glb")
print("Exported scratch/test_tip_out.glb")
