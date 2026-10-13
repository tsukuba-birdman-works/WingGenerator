import sys
import os
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder
import json

# Create a test parameter dictionary
engine = RibGeneratorEngine()
p = {
    'wing_span': 1000.0,
    'interval': 100.0,
    'chord_root': 200.0,
    'chord_tip': 200.0,
    'spar_pos_root': 0.3,
    'spar_pos_tip': 0.3,
    'spar_hole_dia': 20.0,
    'rear_spar_dia': 10.0,
    'rear_spar_dx': 50.0,
    'rear_spar_dx_root': 50.0,
    'rear_spar_dx_tip': 50.0,
    'rear_spar_dy': 0.0,
    'rear_spar_dy_root': 0.0,
    'rear_spar_dy_tip': 0.0,
    'front_spar_dia': 0.0,
    'joint_length': 0.0,
    'margin_outer': 5.0,
    'margin_outer_edge': 5.0,
    'beam_width': 5.0,
    'edge_beam_width': 5.0,
    'te_cut': 2.0,
    'root_bolt1': (0,0,0),
    'root_bolt2': (0,0,0),
    'tip_bolt1': (0,0,0),
    'tip_bolt2': (0,0,0),
    'xb_zones': [],
    'connectors': [(900.0, "V-Shape")],
    'rear_spar_cutoff_act': True,
    'rear_spar_cutoff_start': 500.0,
    'rear_spar_main_conn': 800.0,
    'truss_angles_dict': {},
    'base_truss_angle': 45.0,
    'file1': '',
    'file2': ''
}
p['y_positions'] = list(range(0, 1001, 100))
p['y_ext'] = p['y_positions']

print(f"Generating ribs")
res_list = []
for i, y in enumerate(p['y_positions']):
    res_list.append(engine.generate_rib_at_y(p, y, i, 5.0)[0])

for i, res in enumerate(res_list):
    y = p['y_positions'][i]
    c_m = res[1]
    c_r = res[3]
    hole_r = res[4]
    print(f"Rib at Y={y}: c_m={c_m}, c_r={c_r}, rear_hole_exists={len(hole_r) > 0}")
