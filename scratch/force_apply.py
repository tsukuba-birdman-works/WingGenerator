import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# Z-axis logic replace using regex for robust match
pattern_bool = r"                            if t > 1e-5:.*?                            extended_subs\.append\(sub_ext\)"
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

content = re.sub(pattern_bool, replace_bool, content, flags=re.DOTALL)

with open('core/export_3d.py', 'w') as f:
    f.write(content)

with open('core/engine.py', 'r') as f:
    engine_content = f.read()

engine_content = re.sub(
    r"zones\.append\(\(te_start, max\(0\.0, te_start - f_w\), True\)\)",
    r"zones.append((te_start + f_w, te_start + 0.01, True))",
    engine_content
)

with open('core/engine.py', 'w') as f:
    f.write(engine_content)

print("Applied!")
