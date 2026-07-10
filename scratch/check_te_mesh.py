from core.export_3d import Wing3DExporter

p = {
    'wing_type': 'Right', 'y_positions': [0, 100, 200], 'chord_lengths': [200, 200, 200],
    'washouts': [0, 0, 0], 'dihedrals': [0, 0, 0], 'connectors': [], 'carbon_rib_configs': [],
    'jig_hole_diameter': 5.0, 'te_cut': 20.0, 'spar_x': 50.0, 'spar_y': 5.0,
    'spar_dia': 8.0, 'spar_hole_dia': 8.0, 'joint_length': 0.0, 'rib_thick': 2.0,
    'cr_thick': 1.0, 'cr_act': False, 'wing_span': 200.0,
    'export_te': True, 'export_ribs': True
}

exporter = Wing3DExporter(p)
scene_geoms, analytics = exporter.build_geometry()
te_skin = scene_geoms.get('TE_Skin')
if te_skin:
    print("TE Skin faces:", len(te_skin.faces))
    print("TE Skin watertight?", te_skin.is_watertight)
else:
    print("No TE Skin")
