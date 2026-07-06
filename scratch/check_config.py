from core.engine import RibGeneratorEngine
import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

# Check pm vars
print("jig_y_positions in vars:", 'jig_y_positions' in app.pm.vars)
print("jig_y_positions value:", app.pm.vars['jig_y_positions'].get())

all_vars = app.get_all_vars()
print("jig_y_positions in get_all_vars:", 'jig_y_positions' in all_vars)
print("jig_base_height in get_all_vars:", 'jig_base_height' in all_vars)
