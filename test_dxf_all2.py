import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from core.export_dxf import WingDXFExporter

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
ui.y_positions = [0, 50]
params = ui._get_builder_params()
params['file1'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
params['file2'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
params['te_cut'] = 5.0

def inspect_jig(p):
    import numpy as np
    chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = ui.engine.get_local_params(p, 50.0)
    te_cut = p.get('te_cut', 0.0)
    pts1 = ui.engine.load_dat(p['file1'])
    pts2 = ui.engine.load_dat(p['file2'])
    n_pts = 300
    blended = ui.engine.resample_airfoil(pts1, n_pts)
    scaled = blended * chord
    le_idx = np.argmin(scaled[:, 0])
    l_x = scaled[le_idx:, 0]
    te_support_start_x = chord - te_cut - 10.0
    print(f"Chord: {chord}, te_cut: {te_cut}, te_support_start_x: {te_support_start_x}")
    print(f"l_x min: {np.min(l_x)}, l_x max: {np.max(l_x)}")
    
inspect_jig(params)
