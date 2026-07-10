import re

with open('core/engine.py', 'r') as f:
    content = f.read()

search = """                    te_unrot = np.column_stack((
                        np.concatenate((te_u_x, te_l_x[1:])),
                        np.concatenate((te_u_y, te_l_y[1:]))
                    ))"""

replace = """                    te_unrot = np.column_stack((
                        np.concatenate((te_u_x, te_l_x)),
                        np.concatenate((te_u_y, te_l_y))
                    ))"""

if search in content:
    content = content.replace(search, replace)
    with open('core/engine.py', 'w') as f:
        f.write(content)
    print("Fixed engine.py te_l_x concatenation")
else:
    print("Could not find search block")
