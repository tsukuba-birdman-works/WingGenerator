import numpy as np
import sys
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
import tkinter as tk
from ui.app import RibGeneratorApp
root = tk.Tk()
app = RibGeneratorApp(root)
app.update()
app.chord_var.set(1000.0)
app.plank_enabled_var.set(True)
app._generate_rib()
app._open_fea_window()
fea = app.fea_window
fea.plank_enabled_var.set(True)
fea.str_enabled_var.set(False)
fea._run_analysis()
md = fea.engine.mesh_data
rib_nodes = set(md['triNodesRib'].flatten())
plank_nodes = set(md['triNodesPlank'].flatten())
shared = rib_nodes.intersection(plank_nodes)
print(f"Rib nodes: {len(rib_nodes)}")
print(f"Plank nodes: {len(plank_nodes)}")
print(f"Shared nodes: {len(shared)}")
