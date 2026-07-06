import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import matplotlib
matplotlib.use('Agg')

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

# Mock some values so that we can calculate positions
app.pm.vars['wing_span'].set("500")
app.pm.vars['interval'].set("100")
app.file1_path.set("preset/01_root.dat")
app.file2_path.set("preset/02_tip.dat")
app.pm.vars['jig_y_positions'].set("0, 50, 100")

app.calculate_y_positions()

# Find jig item
jig_idx = -1
for i, item in enumerate(app.preview_items):
    if item.get('type') == 'jig':
        jig_idx = i
        break

if jig_idx != -1:
    print(f"Selecting item {jig_idx}: {app.preview_items[jig_idx]}")
    app.current_rib_idx.set(jig_idx)
    app.update_preview_full()
    app.fig.savefig('scratch/test_jig_preview.png')
    print("Preview generated and saved to scratch/test_jig_preview.png.")
else:
    print("No jig item found.")
