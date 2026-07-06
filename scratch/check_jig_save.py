import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

app.pm.vars['jig_y_positions'].set("123, 456")
app.pm.vars['jig_base_height'].set("999")

vars_dict = app.get_all_vars()
print("jig_y_positions in saved dict:", vars_dict['jig_y_positions'].get())
print("jig_base_height in saved dict:", vars_dict['jig_base_height'].get())
