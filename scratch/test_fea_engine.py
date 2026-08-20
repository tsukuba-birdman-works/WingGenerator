import sys, os
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from core.engine import RibGeneratorEngine
from core.fea_engine import RibFEAEngine
from shapely.geometry import Polygon

engine = RibGeneratorEngine()
params = {
    'chord': 1000.0,
    'thickness': 5.0,
    'spar_x': 300.0, 'spar_y': 0.0, 'spar_d': 40.0,
    'front_spar_x': 100.0, 'front_spar_y': 0.0, 'front_spar_d': 20.0,
    'rear_spar_x': 700.0, 'rear_spar_y': 0.0, 'rear_spar_d': 20.0,
    'washout': 0.0, 'te_cut': 0.0,
    'plank_start': 0.0, 'plank_end': 100.0, 'plank_thick': 2.0,
    'safe_margin_var': False,
    'stringers_data': [],
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
print("Rib generated.")

fea = RibFEAEngine()
poly = Polygon(res.final_rib_mod, res.holes).buffer(0)
plank_poly = Polygon(res.plank_poly_rot).buffer(0) if len(res.plank_poly_rot) > 2 else None

print("Plank poly is valid?", plank_poly.is_valid if plank_poly else False)

inp = fea.generate_fea_model(
    poly, [(300,0)], 1000.0, {'E':15.0, 'nu':0.3}, 5.0,
    mesh_size=5.0,
    stringer_pts_list=[], stringer_params={},
    plank_poly=plank_poly, plank_params={'enabled': True, 'E': 3000.0, 'width': 100.0}
)
print("INP generated at:", inp)
os.system(f"ccx {os.path.splitext(os.path.basename(inp))[0]}")
