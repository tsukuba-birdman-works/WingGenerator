import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """                            # 少し上下（Z）に大きくして表面を確実に突き抜けるようにする
                            # が、TE_Capは斜めなので単純Zスケールは危険。とりあえずそのまま追加。
                            extended_subs.append(cap_cutter)"""

replace = """                            # 少し上下（Z）に大きくして表面を確実に突き抜けるようにする
                            import numpy as np
                            z_min, z_max = cap_cutter.bounds[:, 2]
                            z_center = (z_min + z_max) / 2.0
                            t1 = np.eye(4); t1[2, 3] = -z_center
                            s_mat = np.eye(4); s_mat[2, 2] = 1.05
                            t2 = np.eye(4); t2[2, 3] = z_center
                            cap_cutter.apply_transform(t2 @ s_mat @ t1)
                            extended_subs.append(cap_cutter)"""

if search in content:
    content = content.replace(search, replace)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched TE Cap scale!")
else:
    print("Could not find search block")
