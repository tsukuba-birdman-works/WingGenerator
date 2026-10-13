import sys
import os
import glob
import numpy as np
sys.path.append(os.getcwd())

from core.engine import RibGeneratorEngine
from ui.param_spec import BATCH_PARAMS

dats = glob.glob('**/*.dat', recursive=True)
dat_file = dats[0] if dats else ''

defaults = {item['id']: item.get('default') for item in BATCH_PARAMS}
p = defaults.copy()
p.update({
    'wing_span': 1000.0,
    'interval': 100.0,
    'chord_root': 400.0,
    'chord_tip': 400.0,
    'spar_pos_root': 30.0,
    'spar_pos_tip': 30.0,
    'spar_hole_dia': 20.0,
    'spar_hole_dv': 20.0,
    'rear_spar_dia': 12.0,
    # spar_x = 120. rear_dx = 180 -> x = 300 (75% of 400mm chord)
    'rear_spar_dx': 180.0,
    'rear_spar_dx_root': 180.0,
    'rear_spar_dx_tip': 180.0,
    'rear_spar_dy': 0.0,
    'rear_spar_dy_root': 0.0,
    'rear_spar_dy_tip': 0.0,
    'front_spar_dia': 0.0,
    'joint_length': 0.0,
    'margin_outer': 5.0,
    'margin_outer_edge': 5.0,
    'margin_spar': 3.0,
    'margin_bolt': 3.0,
    'min_hole_dia': 5.0,
    'beam_width': 5.0,
    'edge_beam_width': 5.0,
    'te_cut': 0.0,
    'root_bolt1': (0,0,0),
    'root_bolt2': (0,0,0),
    'tip_bolt1': (0,0,0),
    'tip_bolt2': (0,0,0),
    'xb_zones': [],
    'connectors': [],
    'rear_spar_cutoff_act': False,
    'truss_angles_dict': {},
    'base_truss_angle': 45.0,
    'truss_front_n': 3,
    'truss_rear_n': 4,
    'truss_fillet': 1.0,
    'file1': dat_file,
    'file2': dat_file,
    'blend_ratio_root': 0.0,
    'blend_ratio_tip': 1.0,
    'safe_margin_var': True,
    'rib_thick': 5.0,
    'te_balsa_act': True,
    # TE balsa from 65% to 100%: rear spar at 75% is completely inside TE balsa
    'te_balsa_start': -65.0,
    'te_balsa_end': 65.0,
    'te_balsa_thick': 1.5,
    'plank_start': 0.0,
    'plank_end': 30.0,
    'plank_thick': 1.5,
    'stringers_data': [],
    'te_cap_uf_act': False, 'te_cap_uf_w': 0.0,
    'te_cap_ur_act': False, 'te_cap_ur_w': 0.0,
    'te_cap_lf_act': False, 'te_cap_lf_w': 0.0,
    'te_cap_lr_act': False, 'te_cap_lr_w': 0.0,
    'te_cap_thick': 0.0,
    'rc1_act': False, 'rc1_start': 0, 'rc1_end': 0, 'rc1_thick': 0,
    'rc2_act': False, 'rc2_start': 0, 'rc2_end': 0, 'rc2_thick': 0,
    'xbrace_dia': 2.0,
    'carbon_rib_configs': [],
    'wing_type': 'Right',
})
p['y_positions'] = [200.0]
p['y_ext'] = [200.0]

engine = RibGeneratorEngine()
res = engine.generate_rib_at_y(p, 200.0, 0, 5.0)

print("te_balsa_pts is not None:", res.te_balsa_pts is not None)
print("te_balsa_holes count:", len(res.te_balsa_holes) if res.te_balsa_holes else 0)
if res.te_balsa_holes:
    for i, h in enumerate(res.te_balsa_holes):
        print(f"  Hole {i}: shape={h.shape}, center={np.mean(h, axis=0)}")
        c_r = res.c_r
        dist = np.linalg.norm(np.mean(h, axis=0) - c_r)
        print(f"  Distance from hole center to c_r: {dist:.4f} mm")
        assert dist < 0.5, "Hole should be centered at c_r"

print("Internal hole test PASSED!")
