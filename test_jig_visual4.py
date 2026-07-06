import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import matplotlib.pyplot as plt

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
params['front_spar_dia'] = 8.0
params['front_spar_dx'] = -30.0
params['rear_spar_dia'] = 6.0
params['rear_spar_dx'] = 50.0
params['washout_tip'] = -5.0
params['jig_pillar_angle'] = 80.0

jig_data = ui.engine.generate_jig_at_y(params, 1000.0, return_full=True)
if jig_data and 'jig_pts' in jig_data:
    xs, ys = zip(*(jig_data['jig_pts'] + [jig_data['jig_pts'][0]]))
    plt.figure()
    plt.plot(xs, ys, label='Jig')
    w_x, w_y = zip(*(jig_data['wing_pts'] + [jig_data['wing_pts'][0]]))
    plt.plot(w_x, w_y, 'k--', label='Wing')
    plt.axis('equal')
    plt.legend()
    plt.savefig('scratch/test_jig_visual_fix4.png')
    print("Saved scratch/test_jig_visual_fix4.png")
else:
    print("Preview Failed")
