import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """        rib_sub_meshes = ribs_m_list + carbon_m_list
        for name, m in other_meshes.items():
            if m is not None:
                if name == "TE_Skin" and rib_sub_meshes:
                    extended_subs = []
                    for sub in rib_sub_meshes:
                        try:
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
                                s_mat[0, 0] = 1.0   # X方向（前後）には伸ばさない（削られすぎ防止）
                                s_mat[1, 1] = scale # Y方向（幅）を広げる
                                s_mat[2, 2] = 1.05  # Z方向（上下）に十分に伸ばして薄皮を防ぐ

                                t2 = np.eye(4)
                                t2[0, 3] = x_center
                                t2[1, 3] = y_center
                                t2[2, 3] = z_center

                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                            extended_subs.append(sub_ext)"""

replace = """        # Use Cutter meshes if available (which are already buffered by +1mm in Z)
        cutter_m_list = [m for m, k in meshes if k in ['Ribs_Cutter', 'CarbonRibs_Cutter']]
        rib_sub_meshes = cutter_m_list if cutter_m_list else ribs_m_list + carbon_m_list

        for name, m in other_meshes.items():
            if m is not None:
                if name == "TE_Skin" and rib_sub_meshes:
                    extended_subs = []
                    for sub in rib_sub_meshes:
                        try:
                            sub_ext = sub.copy()
                            y_min, y_max = sub_ext.bounds[:, 1]
                            y_center = (y_min + y_max) / 2.0
                            t = y_max - y_min
                            if t > 1e-5:
                                scale = (t + 2.0) / t
                                t1 = np.eye(4)
                                t1[1, 3] = -y_center
                                s_mat = np.eye(4)
                                s_mat[1, 1] = scale # Y方向のみ拡大
                                t2 = np.eye(4)
                                t2[1, 3] = y_center
                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                            extended_subs.append(sub_ext)"""

if search in content:
    content = content.replace(search, replace)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched boolean cut!")
else:
    print("Could not find search block")
