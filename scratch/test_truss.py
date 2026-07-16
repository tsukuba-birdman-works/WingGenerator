import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine
import numpy as np

# Mock UI param dict
p = {
    'chord_root': 200, 'chord_tip': 200, 'wing_type': 'Right', 'spar_pos_root': 30, 'spar_pos_tip': 30,
    'file1_path': '', 'file2_path': '',
    'washout_root': 0, 'washout_tip': 0, 'joint_length': 0, 'rib_interval': 100,
    'truss_front_n': 3, 'truss_rear_n': 3, 'beam_width': 5, 'margin_spar': 2, 'margin_bolt': 2, 'margin_outer': 2,
    'truss_fillet': 1, 'min_hole_dia': 1, 'plank_start': 0, 'plank_end': 0, 'plank_thick': 1, 'stringers_data': [],
    'te_cap_uf_act': False, 'te_cap_uf_w': 0, 'te_cap_ur_act': False, 'te_cap_ur_w': 0,
    'te_cap_lf_act': False, 'te_cap_lf_w': 0, 'te_cap_lr_act': False, 'te_cap_lr_w': 0,
    'te_cap_thick': 0, 'rc1_act': False, 'rc1_start': 0, 'rc1_end': 0, 'rc1_thick': 0,
    'rc2_act': False, 'rc2_start': 0, 'rc2_end': 0, 'rc2_thick': 0,
    'rear_spar_dia': 5, 'front_spar_dia': 5, 'spar_hole_dia': 10, 'safe_margin_var': False,
    'truss_scale_front': '0.5, 0.5', 'truss_scale_rear': '0.1', 'fast_mode': True
}

engine = RibGeneratorEngine()
# let's just test parsing
truss_scale_front_list=[float(x) for x in str(p.get('truss_scale_front', '')).split(',') if x.strip()]
truss_scale_rear_list=[float(x) for x in str(p.get('truss_scale_rear', '')).split(',') if x.strip()]
print("Parsed front:", truss_scale_front_list)
print("Parsed rear:", truss_scale_rear_list)
