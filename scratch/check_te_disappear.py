from core.export_3d import Wing3DExporter

p = {
    'wing_type': 'Right', 'y_positions': [0, 100], 'chord_lengths': [200, 200],
    'washouts': [0, 0], 'dihedrals': [0, 0], 'connectors': [], 'carbon_rib_configs': [],
    'jig_hole_diameter': 5.0, 'te_cut': 20.0, 'spar_x': 50.0, 'spar_y': 5.0,
    'spar_dia': 8.0, 'spar_hole_dia': 8.0, 'joint_length': 0.0, 'rib_thick': 2.0,
    'cr_thick': 1.0, 'cr_act': False, 'wing_span': 100.0,
    'export_te': True, 'export_ribs': True,
    'te_caps': [{'start': 0, 'end': 1, 'act': True, 'u_f_act': True, 'u_f_w': 5.0, 'u_r_act': False, 'l_f_act': False, 'l_r_act': False, 'thick': 1.0}]
}

exporter = Wing3DExporter()
exporter.p = p
from core.engine import RibGeneratorEngine
exporter.engine = RibGeneratorEngine()
scene_rib_data, plank_curves, te_curves, stringer_curves, film_curves, te_cap_curves, main_spar_centers, rear_spar_centers, front_spar_centers = exporter._collect_geometry_data()

print("TE curves length:", len(te_curves))
for i, curve in enumerate(te_curves):
    print(f"TE curve {i}: {len(curve) if curve is not None else 'None'}")
    
scene_geoms, _ = exporter.build_geometry()
te_skin = scene_geoms.get('TE_Skin')
if te_skin:
    print("TE Skin faces:", len(te_skin.faces))
else:
    print("No TE Skin generated!")
