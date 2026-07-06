import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from core.export_dxf import WingDXFExporter
import traceback
import sys

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
ui.y_positions = [0, 50]
ui.tabs_active = tk.BooleanVar(value=False)

try:
    params = ui._get_builder_params()
    params['dxf_all_in_one'] = True
    params['dxf_target_jigs'] = True
    params['dxf_target_ribs'] = True
    params['dxf_target_carbon'] = False
    params['jig_y_positions'] = "0, 50"
    params['joint_length'] = 0.0
    
    exporter = WingDXFExporter(ui.engine, params)
    exporter.export_all_ribs("/tmp")
    print("Success")
except Exception as e:
    traceback.print_exc()
