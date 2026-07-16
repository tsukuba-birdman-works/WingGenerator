import re

# 1. export_3d.py のカッター前面延長
with open('core/export_3d.py', 'r') as f:
    content = f.read()

search_cutter = """                                inflated_p = p_simp.buffer(1.0)
                                minx, miny, maxx, maxy = p_simp.bounds
                                bbox = box(minx, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)"""

replace_cutter = """                                inflated_p = p_simp.buffer(1.0)
                                minx, miny, maxx, maxy = p_simp.bounds
                                # 前縁側(minx)を2mm伸ばして後縁ブロックとCoplanarになるのを防ぐ
                                bbox = box(minx - 2.0, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)"""

if search_cutter in content:
    content = content.replace(search_cutter, replace_cutter)

# 2. export_3d.py のキャップ法線反転
search_cap = """            cap1 = make_cap(aligned_curves[0], flip_normal=True)
            cap2 = make_cap(aligned_curves[-1], flip_normal=False)"""

replace_cap = """            cap1 = make_cap(aligned_curves[0], flip_normal=False)
            cap2 = make_cap(aligned_curves[-1], flip_normal=True)"""

if search_cap in content:
    content = content.replace(search_cap, replace_cap)

# 3. export_3d.py のブーリアン処理（不要なZスケールを削除し、Yスケールのみに）
search_bool = """                                s_mat[0, 0] = 1.02  # 少し前後に伸ばして薄皮を防ぐ
                                s_mat[1, 1] = scale # 幅を広げる
                                s_mat[2, 2] = 1.02  # 少し上下に伸ばして薄皮を防ぐ"""

replace_bool = """                                s_mat[0, 0] = 1.0
                                s_mat[1, 1] = scale # Y方向のみ拡大
                                s_mat[2, 2] = 1.0"""

if search_bool in content:
    content = content.replace(search_bool, replace_bool)

with open('core/export_3d.py', 'w') as f:
    f.write(content)

print("All fixes applied directly.")
