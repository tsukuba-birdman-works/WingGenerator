import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import matplotlib
matplotlib.use('Agg')

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

app.pm.vars['jig_y_positions'] = tk.StringVar(value="0, 50, 100")
app.calculate_y_positions()
print([i['label'] for i in app.preview_items])
