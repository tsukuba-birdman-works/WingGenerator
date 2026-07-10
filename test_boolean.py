import sys
import json
import numpy as np
import trimesh
sys.path.append('.')
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter

try:
    with open('26_htail.json', 'r') as f:
        j = json.load(f)
    params = {}
    for k, v in j.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    params.update(vv)
                else:
                    params[kk] = vv
        else:
            params[k] = v
except:
    pass

import glob
dats = glob.glob('Airfoils/*.dat')
if dats:
    params['file1_path'] = dats[0]
    params['file2_path'] = dats[0]

engine = RibGeneratorEngine()
exporter = Wing3DExporter()
exporter.p = params
exporter.engine = engine
res = exporter._collect_geometry_data()
scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm = res

# check meshes
ribs_m_list = []
carbon_m_list = []

def create_extrusion(p_simp, thickness, y_global):
    mesh = trimesh.creation.extrude_polygon(p_simp, height=thickness)
    swap_yz = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    mesh.apply_transform(swap_yz)
    mesh.apply_translation([0, y_global, 0])
    return mesh

from shapely.geometry import Polygon
for data in scene_rib_data:
    if len(data) == 5:
        y_global, thickness, ext_pts, holes, mat_key = data
        p = Polygon(ext_pts)
        if p.is_valid and not p.is_empty:
            m = create_extrusion(p, thickness, y_global)
            if mat_key == 'Ribs': ribs_m_list.append(m)
            elif mat_key == 'CarbonRibs': carbon_m_list.append(m)

print("Ribs:", len(ribs_m_list), "Carbon:", len(carbon_m_list))
rib_sub_meshes = ribs_m_list + carbon_m_list

if "TE_Skin" in other_meshes and other_meshes["TE_Skin"] is not None:
    m = other_meshes["TE_Skin"]
    print("TE_Skin loaded, bounds:", m.bounds)
    extended_subs = []
    for i, sub in enumerate(rib_sub_meshes):
        sub_ext = sub.copy()
        y_min, y_max = sub_ext.bounds[:, 1]
        y_center = (y_min + y_max) / 2.0
        t = y_max - y_min
        if t > 1e-5:
            scale = (t + 2.0) / t
            x_min, x_max = sub_ext.bounds[:, 0]
            z_min, z_max = sub_ext.bounds[:, 2]
            x_center = (x_min + x_max) / 2.0
            z_center = (z_min + z_max) / 2.0

            t1 = np.eye(4)
            t1[0, 3] = -x_center
            t1[1, 3] = -y_center
            t1[2, 3] = -z_center

            s_mat = np.eye(4)
            s_mat[0, 0] = 1.0
            s_mat[1, 1] = scale
            s_mat[2, 2] = 1.02

            t2 = np.eye(4)
            t2[0, 3] = x_center + 0.5
            t2[1, 3] = y_center
            t2[2, 3] = z_center

            mat = t2 @ s_mat @ t1
            sub_ext.apply_transform(mat)
        extended_subs.append(sub_ext)
        if i == len(rib_sub_meshes) - 1:
            print("Tip rib cutter bounds:", sub_ext.bounds)
    
    try:
        combined_sub = trimesh.util.concatenate(extended_subs)
        diff = Wing3DExporter.blender_difference(m, combined_sub)
        print("Diff succeeded, faces:", len(diff.faces))
        diff.export('test_te_diff.glb')
    except Exception as e:
        print("Diff failed:", e)

