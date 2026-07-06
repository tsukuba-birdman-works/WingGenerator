import tkinter as tk
from ui.batch_mode import BatchModeUI
from core.engine import RibGeneratorEngine
from ui.param_spec import PM

root = tk.Tk()
engine = RibGeneratorEngine()
pm = PM()
ui = BatchModeUI(root, engine, pm)

ui.pm.vars['wing_span'].set('1000.0')
ui.pm.vars['spar_pos_root'].set('0.3')
ui.pm.vars['spar_pos_tip'].set('0.3')
ui.pm.vars['dxf_part_plank'].set(False)

params = ui._get_builder_params()
print("wing_span:", params.get('wing_span'))
print("dxf_part_plank:", params.get('dxf_part_plank'))
print("dxf_start_idx:", params.get('dxf_start_idx'))
print("dxf_end_idx:", params.get('dxf_end_idx'))
