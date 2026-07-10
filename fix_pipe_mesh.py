import re

with open('core/export_3d.py', 'r') as f:
    text = f.read()

# Fix generate_pipe_mesh normals
old_faces_logic = """                    # 外側の面
                    faces.append([p_idx, s_idx, p_next_idx])
                    faces.append([p_next_idx, s_idx, s_next_idx])
                    # 内側の面（法線が内側を向くように順序を逆にする）
                    faces.append([p_idx + 1, p_next_idx + 1, s_idx + 1])
                    faces.append([p_next_idx + 1, s_next_idx + 1, s_idx + 1])"""

new_faces_logic = """                    # 外側の面 (法線が外を向くように)
                    faces.append([p_idx, p_next_idx, s_idx])
                    faces.append([p_next_idx, s_next_idx, s_idx])
                    # 内側の面（法線が内側=空洞側を向くように順序を逆にする）
                    faces.append([p_idx + 1, s_idx + 1, p_next_idx + 1])
                    faces.append([p_next_idx + 1, s_idx + 1, s_next_idx + 1])"""

text = text.replace(old_faces_logic, new_faces_logic)

with open('core/export_3d.py', 'w') as f:
    f.write(text)
