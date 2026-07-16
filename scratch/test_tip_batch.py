import sys, os
sys.path.append('.')
from core.export_3d import Wing3DExporter
from core.engine import RibGeneratorEngine
import numpy as np

p = {
    'airfoil_file': 'airfoil/dae51.dat',
    'chord': 200, 'root_chord': 200, 'taper_ratio': 0.3,
    'sweep_angle': 15, 'wing_span': 1000, 'num_ribs': 15,
    'washout': 0, 'base_truss_angle': 0, 'truss_angles_dict': {},
    'te_cut': 20, 'spar_pos': 30, 'front_spar_pos': 15, 'rear_spar_pos': 70,
    'spar_dia': 10, 'front_spar_dia': 6, 'rear_spar_dia': 8,
    'export_te': True, 'export_carbon_ribs': True,
    'te_cap_uf_act': False, 'te_cap_ur_act': False, 'te_cap_lf_act': False, 'te_cap_lr_act': False,
    'te_cut_overlap': 30, 'kerf': 0, 'cut_margin': 0
}

engine = RibGeneratorEngine()
params_list = []
y_positions = np.linspace(0, p['wing_span']/2, p['num_ribs'])
for y in y_positions:
    pp = p.copy()
    pp['y_positions'] = [y]
    pp['chord'] = p['root_chord'] - (p['root_chord'] * (1 - p['taper_ratio']) * (y / (p['wing_span']/2)))
    params_list.append(pp)

# Mock standard exporter behavior
exporter = Wing3DExporter()
exporter.generate_meshes(params_list, "scratch/test_tip_out.glb")
print("Exported scratch/test_tip_out.glb")
