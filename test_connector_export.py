import sys
import numpy as np
from core.export_3d import Wing3DBuilder
from core.engine import RibGeneratorEngine

engine = RibGeneratorEngine()
p = {
    'wing_span': 1000.0, 'chord_root': 200.0, 'chord_tip': 200.0,
    'spar_pos_root': 50.0, 'spar_pos_tip': 50.0, 'washout_root': 0.0, 'washout_tip': 0.0,
    'spar_hole_dia': 10.0, 'front_spar_dia': 0.0, 'rear_spar_dia': 5.0,
    'rear_spar_dx': 20.0, 'rear_spar_dy': 0.0, 'joint_length': 0.0,
    'export_connectors': True, 'mat_connectors': 'Carbon (Black)',
    'connectors': [(100.0, "V-Shape"), (200.0, "Y-Shape")],
    'y_positions': [0.0, 300.0],
    'rib_thick': 3.0, 'xb_zones': [], 'truss_angles_dict': {}, 'base_truss_angle': 60.0,
    'te_cut': 0, 'plank_start': 0, 'plank_end': 0, 'plank_thick': 0, 'margin_bolt': 1.0,
    'cr_thick': 3.0, 'rc1_thick': 0, 'rc2_thick': 0
}

builder = Wing3DBuilder(engine, p)
builder.build_geometry()
import trimesh
scene = trimesh.Scene()
for k, m in builder.meshes.items():
    if "Connector" in k:
        scene.add_geometry(m)
scene.export("scratch/test_connectors.glb")
print("Exported to scratch/test_connectors.glb")
