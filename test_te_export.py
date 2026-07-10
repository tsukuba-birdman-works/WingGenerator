import sys
import os
import json
import numpy as np
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter
from core.materials import AVAILABLE_MATERIALS

# Default params that create a standard wing
params = {
    'wing_span': 200,
    'y_positions': [0, 50, 100, 150, 200],
    'rib_thick': 2.0,
    'joint_length': 0.0,
    'wing_type': 'Left',
    'carbon_rib_configs': [],
    'spar_hole_dia': 10,
    'spar_hole_dv': 10,
    'front_spar_dia': 0,
    'rear_spar_dia': 0,
    'te_cut': 10,  # 10 mm from TE
    'te_cut_tip': 10,
    'file1_path': 'Airfoils/NACA0012.dat', 
    'file2_path': 'Airfoils/NACA0012.dat',
    'root_chord': 200,
    'tip_chord': 100,
    'sweep_angle': 0,
    'washout_angle': 0,
    'washout_start': 0,
    'export_te': True,
    'export_te_caps': False,
    'export_plank': False,
    'export_film': False,
    'export_stringers': False,
    'export_connectors': False,
    'export_diag_spars': False
}

# If user config exists, load it
if os.path.exists('Ribgenerator.json'):
    try:
        with open('Ribgenerator.json', 'r') as f:
            j = json.load(f)
            # Find params from structured dict
            for k, v in j.items():
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        if isinstance(vv, dict):
                            params.update(vv)
                        else:
                            params[kk] = vv
                else:
                    params[k] = v
    except Exception as e:
        print("Error loading config:", e)

# Fix paths if they don't exist
if not os.path.exists(params.get('file1_path', '')):
    # find any dat file
    import glob
    dats = glob.glob('Airfoils/*.dat')
    if dats:
        params['file1_path'] = dats[0]
        params['file2_path'] = dats[0]

engine = RibGeneratorEngine()
te_curves = []
for i, y_local in enumerate(params.get('y_positions', [])):
    res = engine.generate_rib_at_y(params, y_local, i, params.get('rib_thick', 2.0), False, None)
    c_m = np.array([res.spar_x, res.spar_y])
    y_ext = y_local
    if len(res[14]) > 0:
        c = res[14]
        # convert to 3D
        c_rel = c - c_m
        c_3d = np.insert(c_rel, 1, y_ext, axis=1)
        te_curves.append(c_3d)

print("te_curves count:", len(te_curves))
mesh = Wing3DExporter.generate_lofted_surface(te_curves, topo_type='TE_Skin')
if mesh is not None:
    mesh.export('test_te_mesh.glb')
    print("Mesh exported to test_te_mesh.glb. Vertices:", len(mesh.vertices), "Faces:", len(mesh.faces))
    
    # Check if the mesh is valid
    print("Is watertight:", mesh.is_watertight)
    print("Is winding consistent:", mesh.is_winding_consistent)
    print("Is empty:", mesh.is_empty)
else:
    print("Failed to generate mesh")

