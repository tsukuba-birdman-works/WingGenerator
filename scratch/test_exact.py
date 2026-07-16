import sys
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
    'te_cut_overlap': 30, 'kerf': 0, 'cut_margin': 0,
    'joint_length': 0, 'rib_thick': 2.0, 'cr_thick': 2.0,
    'carbon_rib_configs': []
}

engine = RibGeneratorEngine()
params_list = []
y_positions = np.linspace(0, p['wing_span']/2, p['num_ribs'])
for y in y_positions:
    pp = p.copy()
    pp['y_positions'] = [y]
    pp['chord'] = p['root_chord'] - (p['root_chord'] * (1 - p['taper_ratio']) * (y / (p['wing_span']/2)))
    params_list.append(pp)

res_list = [engine.generate_single_rib(pp) for pp in params_list]

exporter = Wing3DExporter()
exporter.p = p
exporter.engine = engine
scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm = exporter.build_scene_geoms(res_list)

te_skin = other_meshes.get("TE_Skin")
if te_skin:
    print(f"TE Skin faces: {len(te_skin.faces)}")
else:
    print("No TE Skin generated!")

