import re

with open('core/engine.py', 'r') as f:
    content = f.read()

search = """            te_part_coords = []
            if final_rib_mod_poly and P_u_rot is not None and P_l_rot is not None:
                main_poly = self.cut_polygon_by_line(final_rib_mod_poly, P_u_rot, P_l_rot, 'left')
                te_poly = self.cut_polygon_by_line(final_rib_mod_poly, P_u_rot_te, P_l_rot_te, 'right')
                final_rib_mod_poly = main_poly
                if getattr(te_poly, 'is_empty', True) == False:
                    te_part_coords = np.array(te_poly.exterior.coords)"""

replace = """            te_part_coords = []
            if final_rib_mod_poly and P_u_rot is not None and P_l_rot is not None:
                main_poly = self.cut_polygon_by_line(final_rib_mod_poly, P_u_rot, P_l_rot, 'left')
                final_rib_mod_poly = main_poly
                
                if te_cut > 0:
                    num_pts = 25
                    te_cut_overlap = te_cut + 10.0
                    u_pts_rev = np.column_stack((u_x_mod[::-1], u_y_mod[::-1]))
                    l_pts_rev = np.column_stack((l_x_mod[::-1], l_y_mod[::-1]))
                    
                    dist_u = np.zeros(len(u_pts_rev))
                    dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))
                    
                    dist_l = np.zeros(len(l_pts_rev))
                    dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))
                    
                    targets_u = np.linspace(0, te_cut_overlap, num_pts)
                    targets_l = np.linspace(te_cut_overlap, 0, num_pts)
                    
                    te_u_x = np.interp(targets_u, dist_u, u_pts_rev[:, 0])
                    te_u_y = np.interp(targets_u, dist_u, u_pts_rev[:, 1])
                    
                    te_l_x = np.interp(targets_l, dist_l, l_pts_rev[:, 0])
                    te_l_y = np.interp(targets_l, dist_l, l_pts_rev[:, 1])
                    
                    te_unrot = np.column_stack((
                        np.concatenate((te_u_x, te_l_x)),
                        np.concatenate((te_u_y, te_l_y))
                    ))
                    
                    te_part_coords = (te_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]"""

if search in content:
    content = content.replace(search, replace)
    with open('core/engine.py', 'w') as f:
        f.write(content)
    print("Patched engine.py again with +10 overlap")
else:
    print("Could not find search block")
