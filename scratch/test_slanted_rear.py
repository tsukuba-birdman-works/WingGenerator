import sys
import os
import numpy as np
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine

engine = RibGeneratorEngine()
p = {
    'wing_span': 1000.0,
    'interval': 100.0,
    'chord_root': 300.0,
    'chord_tip': 200.0,
    'spar_pos_root': 0.3,
    'spar_pos_tip': 0.3,
    'spar_hole_dia': 20.0,
    'rear_spar_dia': 10.0,
    'rear_spar_dx': 100.0,
    'rear_spar_dx_root': 100.0,
    'rear_spar_dx_tip': 80.0,
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
    'connectors': [],
    'rear_spar_cutoff_act': True,
    'rear_spar_cutoff_start': 500.0,
    'rear_spar_main_conn': 800.0,
    'truss_angles_dict': {},
    'base_truss_angle': 45.0,
    'file1': 'airfoils/DAE51.dat',
    'file2': 'airfoils/DAE51.dat',
    'safe_margin_var': True,
    'rib_thick': 5.0,
    'te_balsa_act': True,
    'te_balsa_start': -90.0,
    'te_balsa_end': 90.0,
    'te_balsa_thick': 1.0,
}
p['y_positions'] = list(range(0, 1001, 100))
p['y_ext'] = p['y_positions']

# Test file availability
import os.path
if not os.path.exists('airfoils/DAE51.dat'):
    # Search for an available dat file
    import glob
    dats = glob.glob('**/*.dat', recursive=True)
    if dats:
        p['file1'] = dats[0]
        p['file2'] = dats[0]
        print(f"Using dat file: {dats[0]}")
    else:
        print("No dat file found")

print("Test setup complete")
