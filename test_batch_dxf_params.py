import tkinter as tk
from ui.batch_mode import BatchModeUI
from core.engine import RibGeneratorEngine
from ui.param_spec import PM

root = tk.Tk()
engine = RibGeneratorEngine()
pm = PM()
ui = BatchModeUI(root, engine, pm)

# Simulate filling variables
ui.pm.vars['wing_span'].set('1000.0')
ui.pm.vars['spar_pos_root'].set('0.3')
ui.pm.vars['spar_pos_tip'].set('0.3')
ui.pm.vars['dxf_part_plank'].set(False)

params = ui._get_builder_params()
print("wing_span:", params.get('wing_span'))
print("spar_pos_root:", params.get('spar_pos_root'))
print("dxf_part_plank:", params.get('dxf_part_plank'))
