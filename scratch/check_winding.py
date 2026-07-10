from core.engine import RibGeneratorEngine
import numpy as np

p = {
    'wing_type': 'Right', 'y_positions': [0, 100], 'chord_lengths': [200, 200],
    'washouts': [0, 0], 'dihedrals': [0, 0], 'connectors': [], 'carbon_rib_configs': [],
    'jig_hole_diameter': 5.0, 'te_cut': 20.0, 'spar_x': 50.0, 'spar_y': 5.0,
    'spar_dia': 8.0, 'spar_hole_dia': 8.0, 'joint_length': 0.0, 'rib_thick': 2.0,
    'cr_thick': 1.0, 'cr_act': False
}

engine = RibGeneratorEngine()
res = engine.generate_rib_at_y(p, 0, 0, 2.0, False)
te_part = res[14]
print("TE part top 5 points:", te_part[:5])
print("TE part bottom 5 points:", te_part[-5:])
