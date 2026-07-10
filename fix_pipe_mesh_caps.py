import re

with open('core/export_3d.py', 'r') as f:
    text = f.read()

old_caps = """            # パイプの端に円環状のメッシュを追加して蓋をする
            # 始点の蓋
            for j in range(sections):
                p_idx = j * 2
                p_next_idx = ((j + 1) % sections) * 2
                faces.append([p_idx, p_next_idx, p_idx + 1])
                faces.append([p_next_idx, p_next_idx + 1, p_idx + 1])

            # 終点の蓋
            start_offset = (len(points_3d) - 1) * sections * 2
            for j in range(sections):
                p_idx = start_offset + j * 2
                p_next_idx = start_offset + ((j + 1) % sections) * 2
                faces.append([p_idx, p_idx + 1, p_next_idx])
                faces.append([p_next_idx, p_idx + 1, p_next_idx + 1])"""

new_caps = """            # パイプの端に円環状のメッシュを追加して蓋をする
            # 始点の蓋 (法線が外= -Y 方向を向くように)
            for j in range(sections):
                p_idx = j * 2
                p_next_idx = ((j + 1) % sections) * 2
                faces.append([p_idx, p_idx + 1, p_next_idx])
                faces.append([p_next_idx, p_idx + 1, p_next_idx + 1])

            # 終点の蓋 (法線が外= +Y 方向を向くように)
            start_offset = (len(points_3d) - 1) * sections * 2
            for j in range(sections):
                p_idx = start_offset + j * 2
                p_next_idx = start_offset + ((j + 1) % sections) * 2
                faces.append([p_idx, p_next_idx, p_idx + 1])
                faces.append([p_next_idx, p_next_idx + 1, p_idx + 1])"""

text = text.replace(old_caps, new_caps)

with open('core/export_3d.py', 'w') as f:
    f.write(text)
