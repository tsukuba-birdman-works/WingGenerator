with open('core/export_3d.py', 'r') as f:
    content = f.read()

# 1. Z-axis +-1mm logic
search_bool = """                            if t > 1e-5:
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
                                s_mat[0, 0] = 1.02  # 少し前後に伸ばして薄皮を防ぐ
                                s_mat[1, 1] = scale # 幅を広げる
                                s_mat[2, 2] = 1.02  # 少し上下に伸ばして薄皮を防ぐ

                                t2 = np.eye(4)
                                t2[0, 3] = x_center
                                t2[1, 3] = y_center
                                t2[2, 3] = z_center

                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                            extended_subs.append(sub_ext)"""

replace_bool = """                            if t > 1e-5:
                                scale = (t + 2.0) / t
                                t1 = np.eye(4)
                                t1[1, 3] = -y_center
                                s_mat = np.eye(4)
                                s_mat[1, 1] = scale # Y方向のみ拡大
                                t2 = np.eye(4)
                                t2[1, 3] = y_center
                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                                
                            sub_up = sub_ext.copy()
                            sub_up.apply_translation([0, 0, 1.0])
                            
                            sub_down = sub_ext.copy()
                            sub_down.apply_translation([0, 0, -1.0])
                            
                            extended_subs.extend([sub_ext, sub_up, sub_down])"""

content = content.replace(search_bool, replace_bool)

# 2. Cap normals
search_cap = """            cap1 = make_cap(aligned_curves[0], flip_normal=True)
            cap2 = make_cap(aligned_curves[-1], flip_normal=False)"""

replace_cap = """            cap1 = make_cap(aligned_curves[0], flip_normal=False)
            cap2 = make_cap(aligned_curves[-1], flip_normal=True)"""

content = content.replace(search_cap, replace_cap)

with open('core/export_3d.py', 'w') as f:
    f.write(content)

with open('core/engine.py', 'r') as f:
    engine_content = f.read()

search_zone = """            if f_act and f_w > 0: zones.append((te_start, max(0.0, te_start - f_w), True))"""
replace_zone = """            if f_act and f_w > 0: zones.append((te_start + f_w, te_start + 0.01, True))"""
engine_content = engine_content.replace(search_zone, replace_zone)

with open('core/engine.py', 'w') as f:
    f.write(engine_content)

print("Applied Z-translation logic and fixes.")
