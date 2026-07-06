import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
ui.param_vars['wing_span'].set('1000.0')
ui.param_vars['jig_y_positions'].set('50, 150')
ui.param_vars['export_jigs'].set(True)

try:
    ui.export_dxf()
    print("Export completed!")
except Exception as e:
    import traceback
    traceback.print_exc()

