import sys, os
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from core.engine import RibGeneratorEngine
from core.fea_engine import RibFEAEngine
from shapely.geometry import Polygon, Point
import numpy as np

engine = RibGeneratorEngine()
params = {
    'chord': 1000.0,
    'thickness': 5.0,
    'spar_x': 300.0, 'spar_y': 0.0, 'spar_d': 40.0,
    'front_spar_x': 100.0, 'front_spar_y': 0.0, 'front_spar_d': 20.0,
    'rear_spar_x': 700.0, 'rear_spar_y': 0.0, 'rear_spar_d': 20.0,
    'washout': 0.0, 'te_cut': 0.0,
    'plank_start': 0.0, 'plank_end': 1000.0, 'plank_thick': 2.0,
    'safe_margin_var': False,
    'stringers_data': [
        {'pos': 200, 'w': 10, 'd': 5, 'surf': 'upper', 'type': 'rect', 'use_dxf': False}
    ],
    'te_cap_uf_act': False, 'te_cap_uf_w': 10, 'te_cap_uf_d': 5,
    'te_cap_lf_act': False, 'te_cap_lf_w': 10, 'te_cap_lf_d': 5,
    'te_cap_ur_act': False, 'te_cap_ur_w': 10, 'te_cap_ur_d': 5,
    'te_cap_lr_act': False, 'te_cap_lr_w': 10, 'te_cap_lr_d': 5,
    'rc_cap_uf_act': False, 'rc_cap_uf_w': 10, 'rc_cap_uf_d': 5,
    'rc_cap_lf_act': False, 'rc_cap_lf_w': 10, 'rc_cap_lf_d': 5,
    'rc_cap_ur_act': False, 'rc_cap_ur_w': 10, 'rc_cap_ur_d': 5,
    'rc_cap_lr_act': False, 'rc_cap_lr_w': 10, 'rc_cap_lr_d': 5,
    'fin_type': 'truss', 'fin_angle': 45.0, 'fin_width': 10.0,
    'n_holes': 5, 'hole_margin': 5.0
}
res = engine.generate_rib_at_y(**params)
print("Stringers defined:", len(res.stringers_data))
print("Stringer pts list length:", len(res.stringer_pts_list))

fea = RibFEAEngine()
poly = Polygon(res.final_rib_mod, res.holes).buffer(0)
fea._shapely_to_gmsh(poly, 2.0)

for i, pts in enumerate(res.stringer_pts_list):
    str_poly = Polygon(pts).buffer(2.0 * 0.5)
    str_nodes = []
    for tag, c in zip(fea.mesh_data['nodeTags'], fea.mesh_data['nodeCoords']):
        if tag in fea.mesh_data['outerNodes']:
            if str_poly.contains(Point(c[0], c[1])):
                str_nodes.append(tag)
    print(f"Stringer {i}: Found {len(str_nodes)} nodes")
