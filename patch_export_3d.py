import re

with open("core/export_3d.py", "r") as f:
    content = f.read()

# 1. Update generate_pipe_mesh definition
pipe_mesh_old = """    def generate_pipe_mesh(points_3d, outer_radius, thickness, sections=32):
        \"\"\"
        指定された3D点の経路に沿って、端が閉じていない中空のパイプメッシュを生成します。
        ブーリアン演算を使用せずに、頂点と面から直接メッシュを構築します。
        \"\"\"
        if len(points_3d) < 2 or outer_radius <= thickness:
            return None
        try:
            import trimesh

            inner_radius = outer_radius - thickness"""

pipe_mesh_new = """    def generate_pipe_mesh(points_3d, outer_radius, inner_radius, sections=32):
        \"\"\"
        指定された3D点の経路に沿って、端が閉じていない中空のパイプメッシュを生成します。
        ブーリアン演算を使用せずに、頂点と面から直接メッシュを構築します。
        \"\"\"
        if len(points_3d) < 2 or outer_radius <= inner_radius or inner_radius < 0:
            return None
        try:
            import trimesh"""

content = content.replace(pipe_mesh_old, pipe_mesh_new)

# 2. Update _collect_ribs_and_curves
# Add bolt spacer generation logic
bolt_spacer_logic = """
            # Bolt Spacers
            bolt_inner = self.p.get('bolt_spacer_inner_dia', 3.0) / 2.0
            bolt_len = self.p.get('bolt_spacer_length', 10.0)
            
            if params.get('bolt1_dia', 0) > 0:
                bolt1_outer = params['bolt1_dia'] / 2.0
                cx, cy = res.c_b1[0] - c_m[0], res.c_b1[1] - c_m[1]
                p_start = [cx, y_ext - bolt_len/2.0, cy]
                p_end = [cx, y_ext + bolt_len/2.0, cy]
                spacer_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], bolt1_outer, bolt_inner)
                if spacer_mesh:
                    other_meshes[f"Bolt1_Spacer_{i}"] = spacer_mesh

            if params.get('bolt2_dia', 0) > 0:
                bolt2_outer = params['bolt2_dia'] / 2.0
                cx, cy = res.c_b2[0] - c_m[0], res.c_b2[1] - c_m[1]
                p_start = [cx, y_ext - bolt_len/2.0, cy]
                p_end = [cx, y_ext + bolt_len/2.0, cy]
                spacer_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], bolt2_outer, bolt_inner)
                if spacer_mesh:
                    other_meshes[f"Bolt2_Spacer_{i}"] = spacer_mesh
                    
            # Skins"""
content = content.replace("            # Skins", bolt_spacer_logic)

# 3. Update main/front/rear spar pipe mesh generation
spar_pipe_old = """        spar_thickness = 1.0
        if self.p['export_main_spar']:
            other_meshes["Main_Spar"] = Wing3DExporter.generate_pipe_mesh(main_spar_centers, self.p['spar_hole_dia'] / 2.0, spar_thickness)
        if self.p['export_front_spar']:
            other_meshes["Front_Spar"] = Wing3DExporter.generate_pipe_mesh(front_spar_centers, self.p['front_spar_dia'] / 2.0, spar_thickness)
        if self.p['export_rear_spar']:
            other_meshes["Rear_Spar"] = Wing3DExporter.generate_pipe_mesh(rear_spar_centers, self.p['rear_spar_dia'] / 2.0, spar_thickness)"""

spar_pipe_new = """        if self.p['export_main_spar']:
            inner = self.p.get('main_spar_inner_dia', self.p['spar_hole_dia'] - 2.0) / 2.0
            other_meshes["Main_Spar"] = Wing3DExporter.generate_pipe_mesh(main_spar_centers, self.p['spar_hole_dia'] / 2.0, inner)
        if self.p['export_front_spar']:
            inner = self.p.get('front_spar_inner_dia', self.p['front_spar_dia'] - 2.0) / 2.0
            other_meshes["Front_Spar"] = Wing3DExporter.generate_pipe_mesh(front_spar_centers, self.p['front_spar_dia'] / 2.0, inner)
        if self.p['export_rear_spar']:
            inner = self.p.get('rear_spar_inner_dia', self.p['rear_spar_dia'] - 2.0) / 2.0
            other_meshes["Rear_Spar"] = Wing3DExporter.generate_pipe_mesh(rear_spar_centers, self.p['rear_spar_dia'] / 2.0, inner)"""
content = content.replace(spar_pipe_old, spar_pipe_new)

# 4. Update X-Brace pipe generation
xbrace_old1 = """                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start_down, p_end_lower], r_conn, 1.0)
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_start_up, p_end_upper], r_conn, 1.0)"""
xbrace_new1 = """                inner = self.p.get('xbrace_inner_dia', r_conn*2 - 2.0) / 2.0
                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start_down, p_end_lower], r_conn, inner)
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_start_up, p_end_upper], r_conn, inner)"""
content = content.replace(xbrace_old1, xbrace_new1)

xbrace_old2 = """                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start, p_end_lower], r_conn, 1.0)
                # 2. その中間点から主桁上面へのパイプ
                p_mid = (p_start + p_end_lower) / 2.0
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_mid, p_end_upper], r_conn, 1.0)"""
xbrace_new2 = """                inner = self.p.get('xbrace_inner_dia', r_conn*2 - 2.0) / 2.0
                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start, p_end_lower], r_conn, inner)
                # 2. その中間点から主桁上面へのパイプ
                p_mid = (p_start + p_end_lower) / 2.0
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_mid, p_end_upper], r_conn, inner)"""
content = content.replace(xbrace_old2, xbrace_new2)

# 5. Update Diagonal Spar pipe generation
diag_old = """                    diag_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], R_diag, 1.0)"""
diag_new = """                    # Use diag1 or diag2 inner dia depending on the diag loop. We don't have the index easily here, so we use diag1 as default.
                    inner = self.p.get('diag1_inner_dia', R_diag*2 - 2.0) / 2.0
                    diag_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], R_diag, inner)"""
content = content.replace(diag_old, diag_new)

with open("core/export_3d.py", "w") as f:
    f.write(content)

print("Patch applied to core/export_3d.py")
