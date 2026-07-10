import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """                            if t > 1e-5:
                                scale = (t + 2.0) / t
                                t1 = np.eye(4)
                                t1[1, 3] = -y_center
                                t1[2, 3] = -z_center

                                s_mat = np.eye(4)
                                s_mat[0, 0] = 1.0   # X方向（前後）には伸ばさない（削られすぎ防止）
                                s_mat[1, 1] = scale # Y方向（幅）を広げる
                                s_mat[2, 2] = 1.05  # Z方向（上下）に十分に伸ばして薄皮を防ぐ

                                t2 = np.eye(4)
                                t2[0, 3] = x_center
                                t2[1, 3] = y_center"""

replace = """                            if t > 1e-5:
                                scale = (t + 2.0) / t
                                t1 = np.eye(4)
                                t1[1, 3] = -y_center
                                s_mat = np.eye(4)
                                s_mat[1, 1] = scale # Y方向のみ拡大
                                t2 = np.eye(4)
                                t2[1, 3] = y_center
                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)"""

# using simple string replace
idx1 = content.find("if t > 1e-5:")
idx2 = content.find("extended_subs.append(sub_ext)", idx1)

if idx1 != -1 and idx2 != -1:
    content = content[:idx1] + replace + "\n                            " + content[idx2:]
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Fixed mangled block")
else:
    print("Could not find bounds")
