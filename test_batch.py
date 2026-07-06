import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

app.pm.vars['wing_span'].set('1000')
app.pm.vars['jig_y_positions'].set('50, 150')
app.pm.vars['export_jigs'].set(True)
app.pm.vars['te_cut'].set('10.0')

try:
    app.export_all()
    print("Export successful without errors.")
except Exception as e:
    import traceback
    traceback.print_exc()

root.destroy()
