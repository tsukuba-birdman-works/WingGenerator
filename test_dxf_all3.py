import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from core.export_dxf import WingDXFExporter
import traceback

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
params = ui._get_builder_params()
params['file1'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
params['file2'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
params['wing_span'] = 1000.0
params['chord_root'] = 250.0
params['chord_tip'] = 200.0
params['spar_pos_root'] = 30.0
params['spar_pos_tip'] = 30.0
params['rear_spar_dx'] = 50.0

try:
    pts = ui.engine.generate_jig_at_y(params, 50.0)
    print(f"Jig generated: {len(pts)} points")
except Exception as e:
    traceback.print_exc()
