import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)

kerf_var = ui.pm.vars.get('foam_cut_kerf')
print(f"kerf var type: {type(kerf_var)}")
if kerf_var:
    print(f"kerf val: {kerf_var.get()}")
