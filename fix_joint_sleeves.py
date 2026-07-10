import re

with open('core/export_3d.py', 'r') as f:
    text = f.read()

# Replace the entire _generate_joint_sleeves method
pattern = r"    def _generate_joint_sleeves\(self, meshes\):.*?(?=    def _to_rel)"

new_method = """    def _generate_joint_sleeves(self, meshes):
        joint_sleeves = self.p.get('joint_sleeves', [])
        if not joint_sleeves: return

        import trimesh
        import numpy as np

        R_in = self.p['spar_hole_dia'] / 2.0

        for i, js in enumerate(joint_sleeves):
            y_start = js['start']
            y_end = js['end']
            if y_start >= y_end:
                y_start, y_end = y_end, y_start

            L = y_end - y_start
            if L <= 0: continue

            R_out = js['out_dia'] / 2.0
            t1 = js['t1']
            t2 = js['t2']

            if R_out <= R_in: continue

            # 楕円対応のパイプ生成ヘルパー (内径楕円、外径真円に対応)
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
                    if foam_mesh: meshes[f"JointSleeve_Foam_{i}"] = foam_mesh
"""

text = re.sub(pattern, new_method, text, flags=re.DOTALL)

with open('core/export_3d.py', 'w') as f:
    f.write(text)
