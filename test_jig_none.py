import sys
from core.engine import RibGeneratorEngine

engine = RibGeneratorEngine()
p = {
    'file1': "airfoils/26_center_XGAG_1.23 _11.61_48.5.dat",
    'file2': "airfoils/26_center_XGAG_1.23 _11.61_48.5.dat",
    'wing_span': 1000,
    'chord_root': 200,
    'chord_tip': 100,
    'spar_pos_root': 30,
    'spar_pos_tip': 30,
    'washout_root': 0,
    'washout_tip': 0,
    'jig_base_height': 100,
    'jig_base_thickness': 25,
    'jig_wall_thickness': 10,
    'jig_pillar_angle': 90,
    'jig_te_stopper_height': 10,
    'jig_slot_interval': 100,
    'jig_slot_width': 3,
    'jig_slot_depth': 10,
    'joint_length': 0,
    'te_cut': 0,
    'front_spar_dia': 0,
    'rear_spar_dia': 0,
    'spar_hole_dia': 0,
    'truss_angles_dict': {}, 'xb_zones': [], 'beam_width': 0, 'base_truss_angle': 45
}

jig_pts = engine.generate_jig_at_y(p, 50.0)
print(f"jig_pts length: {len(jig_pts) if jig_pts else 'None'}")
