from core.engine import RibGeneratorEngine
import numpy as np

p = {
    'wing_type': 'Right', 'y_positions': [0, 100], 'chord_lengths': [200, 200],
    'washouts': [0, 0], 'dihedrals': [0, 0], 'connectors': [], 'carbon_rib_configs': [],
    'jig_hole_diameter': 5.0, 'te_cut': 20.0, 'spar_x': 50.0, 'spar_y': 5.0,
    'spar_dia': 8.0, 'spar_hole_dia': 8.0, 'joint_length': 0.0, 'rib_thick': 2.0,
    'cr_thick': 1.0, 'cr_act': False, 'wing_span': 100.0,
    'chord_root': 200.0, 'chord_tip': 200.0, 'spar_pos_pct': 25.0, 'washout_root': 0, 'washout_tip': 0, 'blend_type': 'Linear',
    'te_caps': [{'start': 0, 'end': 1, 'act': True, 'u_f_act': True, 'u_f_w': 5.0, 'u_r_act': False, 'l_f_act': True, 'l_f_w': 5.0, 'l_r_act': False, 'thick': 1.0}]
}

engine = RibGeneratorEngine()
engine.p = p

# Run get_local_params to get chord etc.
chord, spar_pct, washout, blend, xb_t_list, x_dia = engine.get_local_params(p, 0.0)

# Simulate generate_rib_at_y manually to see what's happening
u_x_mod, u_y_mod, l_x_mod, l_y_mod, chord_points = engine.generate_airfoil(chord, spar_pct)

rib_poly, P_u_rot, P_l_rot, R_mat = engine.apply_leading_trailing_cuts(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 50.0, 5.0, 0.0, 20.0, chord)

if rib_poly:
    print("Initial rib_poly area:", rib_poly.area)

# Apply caps
final_rib_mod_poly, te_cap_pts_list = engine.apply_te_caps(
    rib_poly, u_x_mod, u_y_mod, l_x_mod, l_y_mod, 20.0, 1.0, 50.0, 5.0, R_mat,
    True, 5.0, False, 0.0, True, 5.0, False, 0.0
)

print("After caps rib_poly area:", final_rib_mod_poly.area if final_rib_mod_poly else None)

# Cut TE block
u_pts_rev = np.column_stack((u_x_mod[::-1], u_y_mod[::-1]))
dist_u = np.zeros(len(u_pts_rev))
dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))

l_pts_rev = np.column_stack((l_x_mod[::-1], l_y_mod[::-1]))
dist_l = np.zeros(len(l_pts_rev))
dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))

te_cut_overlap = 20.0 + 10.0
cut_u_x_te = np.interp(te_cut_overlap, dist_u, u_pts_rev[:, 0])
cut_u_y_te = np.interp(te_cut_overlap, dist_u, u_pts_rev[:, 1])
cut_l_x_te = np.interp(te_cut_overlap, dist_l, l_pts_rev[:, 0])
cut_l_y_te = np.interp(te_cut_overlap, dist_l, l_pts_rev[:, 1])

P_u_rot_te = (np.array([cut_u_x_te, cut_u_y_te]) - [50.0, 5.0]).dot(R_mat.T) + [50.0, 5.0]
P_l_rot_te = (np.array([cut_l_x_te, cut_l_y_te]) - [50.0, 5.0]).dot(R_mat.T) + [50.0, 5.0]

print("Cutting TE with line:", P_u_rot_te, P_l_rot_te)

te_poly = engine.cut_polygon_by_line(final_rib_mod_poly, P_u_rot_te, P_l_rot_te, 'right')
print("TE Poly is empty?", getattr(te_poly, 'is_empty', True))
