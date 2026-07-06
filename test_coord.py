import numpy as np
import core.engine
from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)
p = ui._get_builder_params()
p['file1'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['file2'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['wing_span'] = 1000.0
p['chord_root'] = 250.0
p['chord_tip'] = 200.0
p['spar_pos_root'] = 30.0
p['spar_pos_tip'] = 30.0

engine = ui.engine
chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = engine.get_local_params(p, 500)
pts1 = engine.load_dat(p['file1'])
n_pts = 300
blended = engine.resample_airfoil(pts1, n_pts)
scaled = blended * chord
le_idx = np.argmin(scaled[:, 0])
u_x_orig = scaled[:le_idx+1, 0][::-1]
u_y_orig = scaled[:le_idx+1, 1][::-1]
l_x_orig = scaled[le_idx:, 0]
l_y_orig = scaled[le_idx:, 1]

spar_x = chord * (spar_pct / 100.0)
spar_y = (float(np.interp(spar_x, u_x_orig, u_y_orig)) + float(np.interp(spar_x, l_x_orig, l_y_orig))) / 2.0
l_y_at_spar = float(np.interp(spar_x, l_x_orig, l_y_orig))

print("spar_y:", spar_y, "l_y_at_spar:", l_y_at_spar)
print("d_m:", p['spar_hole_dia'])
