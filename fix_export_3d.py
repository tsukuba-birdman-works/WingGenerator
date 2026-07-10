import re

with open('core/export_3d.py', 'r') as f:
    text = f.read()

# 1. Update X-brace to use elliptical wrap
old_xbrace_wrap = """                    # 主桁巻き付け部をトーラス形状に変更
                    wrap_m = Wing3DExporter.generate_torus_mesh(center=[0.0, y_val, 0.0], major_radius=R_main, minor_radius=wire_radius)"""

new_xbrace_wrap = """                    # 主桁巻き付け部を楕円パイプに変更 (主桁形状に合わせる)
                    dh, dv = self.p['spar_hole_dia'], self.p.get('spar_hole_dv', self.p['spar_hole_dia'])
                    if dv <= 0: dv = dh
                    wrap_m = Wing3DExporter.generate_pipe_mesh([[0.0, y_val - wire_radius, 0.0], [0.0, y_val + wire_radius, 0.0]], (dh/2.0 + wire_radius*2, dv/2.0 + wire_radius*2), (dh/2.0, dv/2.0))"""

text = text.replace(old_xbrace_wrap, new_xbrace_wrap)

# 2. Update joint sleeves to support elliptical inner holes and circular outer
old_joint_sleeves = """            # helper to create and place annulus
            def place_annulus(r_min, r_max, height, z_center):
                if r_max <= r_min or height <= 0: return None
                try:
                    mesh = trimesh.creation.annulus(r_min=r_min, r_max=r_max, height=height)
                    # annulus is created along Z-axis. Rotate it to align with Y-axis
                    rot = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
                    mesh.apply_transform(rot)
                    # translation
                    trans = trimesh.transformations.translation_matrix([0, z_center, 0])
                    mesh.apply_transform(trans)
                    return mesh
                except Exception as e:
                    print("Error creating joint sleeve part:", e)
                    return None

            js_type = js.get('type', 'Foam+Cap')

            if js_type == 'Carbon Cylinder':
                # Type 2: Just carbon cloth, inner = R_in, outer = R_out
                skin_mesh = place_annulus(R_in, R_out, L, (y_start + y_end) / 2.0)
                if skin_mesh: meshes[f"JointSleeve_Skin_{i}"] = skin_mesh
            else:
                # Type 1: Foam + Caps
                # 1. Skin (Outer cylinder)
                skin_mesh = place_annulus(R_out - t2, R_out, L, (y_start + y_end) / 2.0)
                if skin_mesh: meshes[f"JointSleeve_Skin_{i}"] = skin_mesh

                # 2. Caps (CFRP Plates)
                if t1 > 0:
                    cap_s = place_annulus(R_in, R_out, t1, y_start + t1 / 2.0)
                    if cap_s: meshes[f"JointSleeve_CapS_{i}"] = cap_s

                    cap_e = place_annulus(R_in, R_out, t1, y_end - t1 / 2.0)
                    if cap_e: meshes[f"JointSleeve_CapE_{i}"] = cap_e

                # 3. Foam (Core)
                foam_L = L - 2 * t1
                if foam_L > 0 and R_out - t2 > R_in:
                    foam_mesh = place_annulus(R_in, R_out - t2, foam_L, (y_start + y_end) / 2.0)
                    if foam_mesh: meshes[f"JointSleeve_Foam_{i}"] = foam_mesh"""

new_joint_sleeves = """            # 楕円対応のパイプ生成ヘルパー (内径楕円、外径真円に対応)
            # generate_pipe_mesh は Y 軸に沿ってパイプを生成する
            def place_elliptical_pipe(r_in_tuple, r_out_tuple, height, y_center):
                if height <= 0: return None
                pts = [[0.0, y_center - height/2.0, 0.0], [0.0, y_center + height/2.0, 0.0]]
                return Wing3DExporter.generate_pipe_mesh(pts, r_out_tuple, r_in_tuple)

            js_type = js.get('type', 'Foam+Cap')
            
            # R_in は楕円なので水平・垂直で分ける
            dh, dv = self.p['spar_hole_dia'], self.p.get('spar_hole_dv', self.p['spar_hole_dia'])
            if dv <= 0: dv = dh
            r_in_ell = (dh / 2.0, dv / 2.0)
            
            # 外径は真円
            r_out_circ = (R_out, R_out)

            if js_type == 'Carbon Cylinder':
                # Type 2: Just carbon cloth, inner = Ellipse, outer = Circle
                skin_mesh = place_elliptical_pipe(r_in_ell, r_out_circ, L, (y_start + y_end) / 2.0)
                if skin_mesh: meshes[f"JointSleeve_Skin_{i}"] = skin_mesh
            else:
                # Type 1: Foam + Caps
                r_skin_in_circ = (R_out - t2, R_out - t2)
                
                # 1. Skin (Outer cylinder) - 完全な真円チューブ
                skin_mesh = place_elliptical_pipe(r_skin_in_circ, r_out_circ, L, (y_start + y_end) / 2.0)
                if skin_mesh: meshes[f"JointSleeve_Skin_{i}"] = skin_mesh

                # 2. Caps (CFRP Plates) - 内側楕円、外側真円
                if t1 > 0:
                    cap_s = place_elliptical_pipe(r_in_ell, r_out_circ, t1, y_start + t1 / 2.0)
                    if cap_s: meshes[f"JointSleeve_CapS_{i}"] = cap_s

                    cap_e = place_elliptical_pipe(r_in_ell, r_out_circ, t1, y_end - t1 / 2.0)
                    if cap_e: meshes[f"JointSleeve_CapE_{i}"] = cap_e

                # 3. Foam (Core) - 内側楕円、外側真円
                foam_L = L - 2 * t1
                if foam_L > 0 and R_out - t2 > max(dh/2.0, dv/2.0):
                    foam_mesh = place_elliptical_pipe(r_in_ell, r_skin_in_circ, foam_L, (y_start + y_end) / 2.0)
                    if foam_mesh: meshes[f"JointSleeve_Foam_{i}"] = foam_mesh"""

text = text.replace(old_joint_sleeves, new_joint_sleeves)

with open('core/export_3d.py', 'w') as f:
    f.write(text)
