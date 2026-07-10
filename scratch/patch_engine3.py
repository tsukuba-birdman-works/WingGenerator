import re

with open('core/engine.py', 'r') as f:
    content = f.read()

search = """                    te_unrot = np.column_stack((
                        np.concatenate((te_u_x, te_l_x)),
                        np.concatenate((te_u_y, te_l_y))
                    ))
                    
                    te_part_coords = (te_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]"""

replace = """                    te_unrot = np.column_stack((
                        np.concatenate((te_u_x, te_l_x)),
                        np.concatenate((te_u_y, te_l_y))
                    ))
                    
                    # Ensure winding order is identical to Shapely's standard (CCW)
                    if SHAPELY_AVAILABLE:
                        try:
                            poly = Polygon(te_unrot)
                            if poly.is_valid and not poly.is_empty:
                                te_unrot = np.array(poly.exterior.coords)
                        except: pass
                    
                    te_part_coords = (te_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]"""

if search in content:
    content = content.replace(search, replace)
    with open('core/engine.py', 'w') as f:
        f.write(content)
    print("Patched engine.py again with Shapely winding check")
else:
    print("Could not find search block")
