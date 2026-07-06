import sys
import numpy as np
import matplotlib.pyplot as plt
from core.engine import RibGeneratorEngine
from ui.param_spec import BATCH_PARAMS

def get_default_params():
    p = {}
    for spec in BATCH_PARAMS:
        if 'default' in spec:
            p[spec['id']] = spec['default']
    return p

engine = RibGeneratorEngine()
p = get_default_params()
p['file1'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['file2'] = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
p['wing_span'] = 1000.0
p['chord_root'] = 250.0
p['chord_tip'] = 200.0
p['spar_pos_root'] = 30.0
p['spar_pos_tip'] = 30.0
p['rear_spar_dx'] = 80.0
p['d_m'] = 10.0
p['d_r'] = 6.0
p['te_cut'] = 5.0
p['jig_base_height'] = 150.0
p['jig_slot_interval'] = 100.0
p['jig_slot_width'] = 3.0
p['jig_slot_depth'] = 10.0
p['washout_root'] = 0.0
p['washout_tip'] = 5.0
p['xb_zones'] = []
p['f_spar_zones'] = []
p['truss_angles_dict'] = {0:0, 1:0}

pts = engine.generate_jig_at_y(p, 500.0)
if pts:
    pts = np.array(pts)
    plt.figure(figsize=(10, 4))
    plt.plot(pts[:, 0], pts[:, 1], 'b-', label='Jig Profile')
    plt.axis('equal')
    plt.legend()
    plt.grid(True)
    plt.savefig('scratch/test_jig_visual_updated.png')
    print(f"Jig generated with {len(pts)} points")
else:
    print("Failed to generate jig points.")
