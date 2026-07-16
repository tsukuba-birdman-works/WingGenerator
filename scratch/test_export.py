import sys
sys.path.append('.')
from core.export_3d import Wing3DExporter
from core.engine import RibGeneratorEngine
import numpy as np

p = {
    'airfoil_file': 'airfoil/dae51.dat',
    'chord': 200, 'root_chord': 200, 'taper_ratio': 0.3,
    'sweep_angle': 30, 'wing_span': 1000, 'num_ribs': 10,
    'washout': 0, 'base_truss_angle': 0, 'truss_angles_dict': {},
    'te_cut': 20, 'spar_pos': 30, 'front_spar_pos': 15, 'rear_spar_pos': 70,
    'spar_dia': 10, 'front_spar_dia': 6, 'rear_spar_dia': 8,
    'export_te': True, 'export_carbon_ribs': True,
    'te_cap_uf_act': False, 'te_cap_ur_act': False, 'te_cap_lf_act': False, 'te_cap_lr_act': False,
    'te_cut_overlap': 30, 'kerf': 0, 'cut_margin': 0,
    'joint_length': 0, 'rib_thick': 2.0, 'cr_thick': 2.0,
    'carbon_rib_configs': [],
    'file1': 'airfoil/dae51.dat', 'file2': '', 'plank_start': 0, 'plank_end': 0, 'plank_thick': 0,
    'stringers_data': [], 'safe_margin_var': False, 'te_cap_uf_w': 5, 'te_cap_ur_w': 5, 'te_cap_lf_w': 5,
    'te_cap_lr_w': 5, 'te_cap_thick': 2, 'rc1_act': False, 'rc1_start': 0, 'rc1_end': 0, 'rc1_thick': 0,
    'rc2_act': False, 'rc2_start': 0, 'rc2_end': 0, 'rc2_thick': 0, 'bolt1_pos': 0, 'bolt1_dia': 0,
    'bolt2_pos': 0, 'bolt2_dia': 0, 'fast_mode': False, 'export_connectors': False, 'export_diag_spars': False,
    'export_xbrace_wires': False, 'export_joint_sleeves': False, 'export_te_caps': False, 'export_rib_caps': False,
}

y_positions = np.linspace(0, p['wing_span']/2, p['num_ribs']).tolist()
p['y_positions'] = y_positions

engine = RibGeneratorEngine()
scene_rib_data, plank_curves, te_curves, stringer_curves, film_curves, te_cap_curves, main_spar_centers, rear_spar_centers, front_spar_centers = engine.export_3d_data(p)

exporter = Wing3DExporter(p)
# We need to construct other_meshes
import trimesh
other_meshes = {}
other_meshes["TE_Skin"] = Wing3DExporter.generate_lofted_surface(te_curves)

# Let's run build_scene_geoms to apply boolean cuts
# Wait, `build_scene_geoms` is called by `exporter`?
# In `ui/single_mode.py`, it does:
# exporter = Wing3DExporter(p)
# scene_rib_data, other_meshes, part_colors, _, _ = exporter.build_scene_geoms(scene_rib_data, other_meshes)
# Wing3DExporter.export_3d_scene(filepath, scene_rib_data, other_meshes, False, part_colors)
res = exporter.build_scene_geoms(scene_rib_data, other_meshes)
scene_rib_data = res[0]
other_meshes = res[1]
part_colors = res[2]

Wing3DExporter.export_3d_scene("scratch/test_out.glb", scene_rib_data, other_meshes, False, part_colors)
print("Done")
