from core.engine import RibGeneratorEngine
import matplotlib.pyplot as plt
import numpy as np

p = {
    'wing_span': 1000, 'chord_root': 200, 'chord_tip': 200, 'washout_root': 0, 'washout_tip': 0,
    'spar_pos_root': 0.3, 'spar_pos_tip': 0.3, 'base_aoa': 0, 'joint_length': 0,
    'margin_outer': 2, 'margin_outer_edge': 2, 'beam_width': 3, 'edge_beam_width': 3,
    'truss_angles_dict': {}, 'base_truss_angle': 45, 'truss_front_n': 2, 'truss_rear_n': 2,
    'margin_spar': 2, 'margin_bolt': 2, 'truss_fillet': 1, 'min_hole_dia': 5,
    'plank_start': 0, 'plank_end': 0, 'plank_part_start': 0, 'plank_part_end': 0, 'plank_thick': 0,
    'stringers_data': [], 'te_cut': 20, 'safe_margin_var': False,
    'te_cap_uf_act': True, 'te_cap_uf_w': 5, 'te_cap_ur_act': False, 'te_cap_ur_w': 0,
    'te_cap_lf_act': True, 'te_cap_lf_w': 5, 'te_cap_lr_act': False, 'te_cap_lr_w': 0,
    'rc_cap_uf_act': False, 'rc_cap_uf_w': 0, 'rc_cap_ur_act': False, 'rc_cap_ur_w': 0,
    'rc_cap_lf_act': False, 'rc_cap_lf_w': 0, 'rc_cap_lr_act': False, 'rc_cap_lr_w': 0,
    'spar_hole_dia': 10, 'spar_hole_dv': 10, 'file1': 'preset/AG35.dat', 'file2': 'preset/AG35.dat',
    'xbraces': [], 'xb_zones': [], 'y_positions': [0], 'connectors': []
}
engine = RibGeneratorEngine()
res = engine.generate_rib_at_y(p, 0, 0, 2)
rib_pts = res[0]
te_block = res[14]
caps = res[22]

plt.figure(figsize=(10, 5))
if len(rib_pts) > 0:
    plt.plot(rib_pts[:,0], rib_pts[:,1], 'k-', label='Rib')
if len(te_block) > 0:
    plt.plot(te_block[:,0], te_block[:,1], 'g-', label='TE Block')
for cap in caps[0]:
    plt.plot(cap[:,0], cap[:,1], 'r-', label='Upper Cap')
for cap in caps[1]:
    plt.plot(cap[:,0], cap[:,1], 'b-', label='Lower Cap')
plt.axis('equal')
plt.xlim(150, 210)
plt.legend()
plt.savefig('scratch/te_cap_inspect.png')
print("Saved to scratch/te_cap_inspect.png")
