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
                    
                    # Reverse winding to match the original Shapely output (CW)
                    te_unrot = te_unrot[::-1]
                    
                    te_part_coords = (te_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]"""

if search in content:
    content = content.replace(search, replace)
    with open('core/engine.py', 'w') as f:
        f.write(content)
    print("Patched engine.py to reverse winding")
else:
    print("Could not find search block")
