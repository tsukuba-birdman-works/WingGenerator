import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import numpy as np

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

chord, spar_pct, washout, x_dia, xb_t_list, f_spar_w = ui.engine.get_local_params(params, 50.0)
te_cut = params.get('te_cut', 0.0)

pts1 = ui.engine.load_dat(params['file1'])
n_pts = 300
blended = ui.engine.resample_airfoil(pts1, n_pts)
scaled = blended * chord
le_idx = np.argmin(scaled[:, 0])
l_x = scaled[le_idx:, 0]

te_support_start_x = chord - te_cut - 10.0
print(f"chord={chord}, te_support_start_x={te_support_start_x}, max(l_x)={np.max(l_x)}")

te_x_arr = []
for i in range(len(l_x)):
    if l_x[i] >= te_support_start_x and l_x[i] <= chord:
        te_x_arr.append(l_x[i])
print(f"te_x_arr len: {len(te_x_arr)}")
