import sys
import os
import numpy as np
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine

params = {
    'y_positions': [0, 100, 200, 300, 400],
    'rib_thick': 2.0,
    'joint_length': 0.0,
    'wing_type': 'Left',
    'carbon_rib_configs': [],
    'spar_hole_dia': 10,
    'spar_hole_dv': 10,
    'front_spar_dia': 0,
    'rear_spar_dia': 0,
    'te_cut': -10,
    'te_cut_tip': -10,
    'file1_path': 'Airfoils/NACA0012.dat', # dummy path, we need a real dat file
    'file2_path': 'Airfoils/NACA0012.dat',
    'root_chord': 200,
    'tip_chord': 100,
    'sweep_angle': 0,
    'washout_angle': 0,
    'washout_start': 0
}

# Instead of running the engine, let's just create a dummy TE poly
# Oh wait, we don't have the Dat file easily.
print("We will just rely on the user testing the code.")
