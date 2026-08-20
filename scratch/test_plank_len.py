import sys, os
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
import tkinter as tk
from ui.app import RibGeneratorApp
root = tk.Tk()
app = RibGeneratorApp(root)
app.update()
app.chord_var.set(1000.0)
app.plank_enabled_var.set(True)
app._generate_rib()
print("Generated.")
app._open_fea_window()
fea = app.fea_window
fea.plank_enabled_var.set(True)
fea.str_enabled_var.set(False)

poly = fea.engine.mesh_data
# wait, engine.mesh_data is populated during generate_fea_model
# let's run it
fea._run_analysis()
md = fea.engine.mesh_data
print("Rib tags length:", len(md['triTagsRib']))
print("Plank tags length:", len(md['triTagsPlank']))
