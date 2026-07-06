import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from fix_jig_logic import generate_jig_at_y_new
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
params['rear_spar_dx'] = 50.0
params['washout_tip'] = -5.0

setattr(ui.engine.__class__, 'generate_jig_at_y', generate_jig_at_y_new)

pts = ui.engine.generate_jig_at_y(params, 1000.0) # tip
if pts:
    xs, ys = zip(*pts)
    plt.figure()
    plt.plot(xs, ys, label='Jig')
    plt.axis('equal')
    plt.legend()
    plt.savefig('scratch/test_jig_visual_fix3.png')
    print("Saved scratch/test_jig_visual_fix3.png")
else:
    print("pts is None")
