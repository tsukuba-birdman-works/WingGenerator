import sys
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder

p = {
    'wing_span': 1000.0,
    'chord_root': 200.0,
    'chord_tip': 200.0,
    'spar_pos_root': 50.0,
    'spar_pos_tip': 50.0,
    'washout_root': 0.0,
    'washout_tip': 0.0,
    'spar_hole_dia': 10.0,
    'front_spar_dia': 5.0,
    'front_spar_dx': -20.0,
    'front_spar_dy': 0.0,
    'rear_spar_dia': 5.0,
    'rear_spar_dx': 20.0,
    'rear_spar_dy': 0.0,
    'plank_start': 0.0,
    'plank_end': 0.0,
    'plank_thick': 0.0,
    'plank_part_start': 0.0,
    'plank_part_end': 0.0,
    'te_cut': 0.0,
    'beam_width': 2.0,
    'edge_beam_width': 2.0,
    'margin_spar': 1.0,
    'margin_bolt': 1.0,
    'margin_outer': 1.0,
    'margin_outer_edge': 1.0,
    'base_truss_angle': 60.0,
    'truss_fillet': 2.0,
    'min_hole_dia': 2.0,
    'rib_thick': 3.0,
    'cr_thick': 3.0,
    'te_cap_thick': 1.0,
    'rc1_start': 0.0,
    'rc1_end': 0.0,
    'rc1_thick': 0.0,
    'rc1_width': 0.0,
    'rc2_start': 0.0,
    'rc2_end': 0.0,
    'rc2_thick': 0.0,
    'rc2_width': 0.0,
    'truss_front_n': 1,
    'truss_rear_n': 1,
    'joint_length': 0.0,
    'xb_zones': [],
    
    'export_connectors': True,
    'mat_connectors': 'Carbon (Black)',
    
    'connectors': [(200.0, "V-Shape"), (400.0, "Y-Shape")],
    'y_positions': [0.0, 500.0],
}

engine = RibGeneratorEngine()
builder = Wing3DBuilder(engine, p)
builder._collect_geometry_data()
builder.build_geometry()
print("Generated connector meshes:")
for key in builder.meshes:
    if "Connector" in key:
        print(key, type(builder.meshes[key]))
        print(len(builder.meshes[key].faces), "faces")
