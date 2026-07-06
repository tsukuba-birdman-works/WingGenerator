import os
import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import traceback

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)

# Set UI parameters
ui.wing_span.set("100")
ui.chord_root.set("100")
ui.chord_tip.set("100")
ui.y_positions = [0, 50]

import numpy as np
t = np.linspace(0, 2*np.pi, 20)
x = 0.5 + 0.5*np.cos(t)
y = 0.1*np.sin(t)
with open("/tmp/dummy.dat", "w") as f:
    f.write("MH43\n")
    for i in range(len(x)):
        f.write(f"{x[i]:.4f} {y[i]:.4f}\n")

ui.file1_path.set("/tmp/dummy.dat")
ui.file2_path.set("/tmp/dummy.dat")

if hasattr(ui, 'pm') and 'jig_y_positions' in ui.pm.vars:
    ui.pm.vars['jig_y_positions'].set("0, 50")
ui.dxf_all_in_one.set(True)
ui.dxf_target_jigs.set(True)
ui.dxf_part_plank.set(False)

# Mock
import tkinter.filedialog as filedialog
filedialog.askdirectory = lambda title: "/tmp"
import tkinter.messagebox as messagebox
def crash(title, msg): raise Exception(f"{title}: {msg}")
messagebox.showerror = crash

ui.export_dxf()

