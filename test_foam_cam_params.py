import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

app.pm.vars['foam_cut_kerf'].set("3.14159")
app.pm.vars['foam_feedrate'].set("420.0")

app.y_positions = [0, 50]
app.rib_thick = tk.StringVar(value="2.0")

# Mock FoamCutterGUI
import ui.foam_mode
class MockFoamCutterGUI:
    def __init__(self, root, root_file=None, tip_file=None, block_width=None, wing_type=None,
                 target_type="Plank", target_thickness=0.0, cut_kerf=1.5, wire_dist=1000.0,
                 offset_x=0.0, offset_y=0.0, entry_x=0.0, entry_y=0.0, feedrate=100.0):
        print(f"MOCK CALLED: cut_kerf={cut_kerf}, feedrate={feedrate}, wire_dist={wire_dist}")
ui.foam_mode.FoamCutterGUI = MockFoamCutterGUI

# Overwrite get_poly
def mock_get_poly(idx): return [(0,0), (1,1), (0,1)], [0.5, 0.5]
app.open_in_foam_cam.__code__ = app.open_in_foam_cam.__code__ # Can't do this easily

# Let's just run the block manually
kerf_val = app.safe_float(app.pm.vars.get('foam_cut_kerf', tk.StringVar(value="1.5")), 1.5)
feedrate_val = app.safe_float(app.pm.vars.get('foam_feedrate', tk.StringVar(value="100.0")), 100.0)
print(f"kerf={kerf_val}, feedrate={feedrate_val}")
