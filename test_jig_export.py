import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk
from core.export_dxf import RibExporterDXF

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
ui.param_vars['wing_span'].set('1000.0')
ui.param_vars['jig_y_positions'].set('50, 150')
ui.param_vars['export_jigs'].set(True)

exporter = RibExporterDXF(ui)
exporter.run_export(ui._get_builder_params())
print("Export completed!")
