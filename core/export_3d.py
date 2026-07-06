import numpy as np

class Wing3DBuilder:
    """
    UIから受け取ったパラメータを元に、翼全体の3Dモデルを構築するクラス。
    """
    def __init__(self, engine, params):
        self.engine = engine
        self.p = params

    def _collect_geometry_data(self):
        """
        3Dジオメトリデータを収集する共通処理。
        戻り値: (scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm)
        """
        from .materials import AVAILABLE_MATERIALS, MATERIAL_PBR_PROPERTIES

        scene_rib_data = []
        main_spar_centers, front_spar_centers, rear_spar_centers = [], [], []
        plank_curves, te_curves, film_curves = [], [], []
        stringer_curves, te_cap_curves = [], []
        rib_orig_pts_list = []  # 各リブのオフセットなし翻型輪郭点列（両面テープ計算用）
        other_meshes = {}

        # 1. 通常リブのジオメトリ情報を生成
        for i, y_local in enumerate(self.p['y_positions']):
            res, c_m, y_ext = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])

            # Ribs
            rel_outline = self._to_rel(res[0], c_m)
            rel_holes = [self._to_rel(h, c_m) for h in [res[2], res[4], res[6], res[16], res[18]] + res[7] + res[8] + res[19] if len(h) > 0]
            scene_rib_data.append((y_local + self.p['joint_length'], self.p['rib_thick'], rel_outline, rel_holes, 'Ribs'))

            # オフセットなし元翻型輪郭（final_rib_orig = res[20]）
            orig_pts = np.array(res.final_rib_orig)
            if len(orig_pts) >= 2:
                rib_orig_pts_list.append(orig_pts)

            # Spars
            main_spar_centers.append([0.0, y_ext, 0.0])
            if self.p['front_spar_dia'] > 0: front_spar_centers.append([res[5][0] - c_m[0], y_ext, res[5][1] - c_m[1]])
            if self.p['rear_spar_dia'] > 0: rear_spar_centers.append([res[3][0] - c_m[0], y_ext, res[3][1] - c_m[1]])


            # Bolt Spacers
            bolt_inner = self.p.get('bolt_spacer_inner_dia', 3.0) / 2.0
            bolt_len = self.p.get('bolt_spacer_length', 10.0)

            is_root = (i == 0)
            is_tip = (i == len(self.p['y_positions']) - 1)
            b1 = self.p.get('root_bolt1', (0,0,0)) if is_root else (self.p.get('tip_bolt1', (0,0,0)) if is_tip else (0,0,0))
            b2 = self.p.get('root_bolt2', (0,0,0)) if is_root else (self.p.get('tip_bolt2', (0,0,0)) if is_tip else (0,0,0))
            
            if b1[2] > 0:
                bolt1_outer = b1[2] / 2.0
                cx, cy = res.c_b1[0] - c_m[0], res.c_b1[1] - c_m[1]
                y_center = y_ext + self.p['rib_thick'] / 2.0
                actual_len1 = min(bolt_len, self.p['rib_thick'])
                p_start = [cx, y_center - actual_len1/2.0, cy]
                p_end = [cx, y_center + actual_len1/2.0, cy]
                spacer_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], bolt1_outer, bolt_inner)
                if spacer_mesh:
                    other_meshes[f"Bolt1_Spacer_{i}"] = spacer_mesh

            if b2[2] > 0:
                bolt2_outer = b2[2] / 2.0
                cx, cy = res.c_b2[0] - c_m[0], res.c_b2[1] - c_m[1]
                y_center = y_ext + self.p['rib_thick'] / 2.0
                actual_len2 = min(bolt_len, self.p['rib_thick'])
                p_start = [cx, y_center - actual_len2/2.0, cy]
                p_end = [cx, y_center + actual_len2/2.0, cy]
                spacer_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], bolt2_outer, bolt_inner)
                if spacer_mesh:
                    other_meshes[f"Bolt2_Spacer_{i}"] = spacer_mesh
                    
            # Skins
            if len(res[13]) > 0: plank_curves.append(np.insert(self._to_rel(res[13], c_m), 1, y_ext, axis=1))
            if len(res[14]) > 0: te_curves.append(np.insert(self._to_rel(res[14], c_m), 1, y_ext, axis=1))
            if len(res[20]) > 0: film_curves.append(np.insert(self._to_rel(res[20], c_m), 1, y_ext, axis=1))

            # Stringers
            if not stringer_curves: stringer_curves = [[] for _ in res[21]]
            for idx, st_pts in enumerate(res[21]):
                if idx < len(stringer_curves): stringer_curves[idx].append(np.insert(self._to_rel(st_pts, c_m), 1, y_ext, axis=1))

            # TE Caps
            if not te_cap_curves: te_cap_curves = [[] for _ in res[22]]
            for idx, cap_pts in enumerate(res[22]):
                if idx < len(te_cap_curves): te_cap_curves[idx].append(np.insert(self._to_rel(cap_pts, c_m), 1, y_ext, axis=1))

            # Rib Caps
            if self.p['export_rib_caps']:
                y_global = y_local + self.p['joint_length']
                rc1_pts, rc2_pts = res[23]
                if self.p['rc1_act'] and self.p['rc1_width'] > 0:
                    y_start = y_global + self.p['rib_thick']/2.0 - self.p['rc1_width']/2.0
                    for pts in rc1_pts: scene_rib_data.append((y_start, self.p['rc1_width'], self._to_rel(pts, c_m), [], 'Rib_Cap'))
                if self.p['rc2_act'] and self.p['rc2_width'] > 0:
                    y_start = y_global + self.p['rib_thick']/2.0 - self.p['rc2_width']/2.0
                    for pts in rc2_pts: scene_rib_data.append((y_start, self.p['rc2_width'], self._to_rel(pts, c_m), [], 'Rib_Cap'))

        # 2. カーボンリブのジオメトリ情報を生成
        if self.p['export_carbon_ribs']:
            self._generate_carbon_ribs_data(scene_rib_data)

        # 3. 各パーツのメッシュを生成
        if self.p['joint_length'] > 0: main_spar_centers.insert(0, [0.0, 0.0, 0.0])
        if self.p['export_main_spar']:
            dh, dv = self.p['spar_hole_dia'], self.p.get('spar_hole_dv', 0.0)
            if dv <= 0: dv = dh
            inner = self.p.get('main_spar_inner_dia', dh - 2.0)
            other_meshes["Main_Spar"] = Wing3DExporter.generate_pipe_mesh(main_spar_centers, (dh / 2.0, dv / 2.0), (inner / 2.0, inner / 2.0))
        if self.p['export_front_spar']:
            inner = self.p.get('front_spar_inner_dia', self.p['front_spar_dia'] - 2.0) / 2.0
            other_meshes["Front_Spar"] = Wing3DExporter.generate_pipe_mesh(front_spar_centers, self.p['front_spar_dia'] / 2.0, inner)
        if self.p['export_rear_spar']:
            inner = self.p.get('rear_spar_inner_dia', self.p['rear_spar_dia'] - 2.0) / 2.0
            other_meshes["Rear_Spar"] = Wing3DExporter.generate_pipe_mesh(rear_spar_centers, self.p['rear_spar_dia'] / 2.0, inner)
        if self.p['export_plank']: other_meshes["Plank_Skin"] = Wing3DExporter.generate_lofted_surface(plank_curves)
        if self.p['export_te']: other_meshes["TE_Skin"] = Wing3DExporter.generate_lofted_surface(te_curves)
        if self.p['export_film']: other_meshes["Film_Skin"] = Wing3DExporter.generate_lofted_surface(film_curves)
        if self.p['export_stringers']:
            for i, s_curves in enumerate(stringer_curves):
                if len(s_curves) >= 2: other_meshes[f"Stringer_{i}"] = Wing3DExporter.generate_lofted_surface(s_curves)
        if self.p['export_te_caps']:
            for i, c_curves in enumerate(te_cap_curves):
                if len(c_curves) >= 2: other_meshes[f"TE_Cap_{i}"] = Wing3DExporter.generate_lofted_surface(c_curves)

        if self.p['export_connectors']: self._generate_connector_meshes(other_meshes, main_spar_centers, rear_spar_centers)
        if self.p['export_diag_spars']: self._generate_diag_spar_meshes(other_meshes, main_spar_centers, rear_spar_centers)
        if self.p['export_xbrace_wires']: self._generate_xbrace_meshes(other_meshes, rear_spar_centers)
        if self.p.get('export_joint_sleeves', True): self._generate_joint_sleeves(other_meshes)

        # 4. 色情報を定義
        def get_mat_props(mat_key, default_rgba=[200, 200, 200, 255]):
            mat_name = self.p.get(mat_key, '')
            rgba = AVAILABLE_MATERIALS.get(mat_name, default_rgba)
            pbr = MATERIAL_PBR_PROPERTIES.get(mat_name, (0.1, 0.5)) # default metallic, roughness
            return (rgba, pbr[0], pbr[1])

        part_colors = {
            'Ribs': get_mat_props('mat_ribs'),
            'Main_Spar': get_mat_props('mat_main_spar', [30,30,30,255]),
            'Front_Spar': get_mat_props('mat_front_spar', [30,30,30,255]),
            'Rear_Spar': get_mat_props('mat_rear_spar', [30,30,30,255]),
            'Plank_Skin': get_mat_props('mat_plank'),
            'TE_Skin': get_mat_props('mat_te'),
            'Connector': get_mat_props('mat_connectors', [30,30,30,255]),
            'Stringer': get_mat_props('mat_stringers'),
            'XBraceWire': get_mat_props('mat_xbrace_wires'),
            'Diag_Spar': get_mat_props('mat_diag_spars', [30,30,30,255]),
            'CarbonRibs': get_mat_props('mat_carbon_ribs', [30,30,30,255]),
            'TE_Cap': get_mat_props('mat_te_caps', [30,30,30,255]),
            'Rib_Cap': get_mat_props('mat_rib_caps', [30,30,30,255]),
            'JointSleeve_Cap': get_mat_props('mat_js_cap', [30, 30, 30, 255]),
            'JointSleeve_Foam': get_mat_props('mat_js_foam', [100, 100, 255, 255]),
            'JointSleeve_Skin': get_mat_props('mat_js_skin', [30, 30, 30, 255]),
            'Film_Skin': get_mat_props('mat_film', [250, 250, 255, 80])
        }

        te_span_mm = self.p.get('wing_span', 0.0)
        return scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm

    def build_geometry(self):
        """
        3Dジオメトリを構築し、メモリ上の辞書形式で返す。
        ファイルへの書き出しは行わない。

        Returns
        -------
        scene_geoms : dict {name: trimesh.Trimesh}
        analytics   : dict {
            'rib_perimeters_mm': List[float],  各リブ翻型周長 [mm]
            'te_span_mm': float,               翼スパン長 [mm]
            'main_spar_span_mm': float,        主桦スパン長 [mm]
        }
        """
        scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm = self._collect_geometry_data()
        is_left = self.p['wing_type'] == "Left"
        rib_data_to_export = [d for d in scene_rib_data if d[-1] != 'Ribs' or self.p.get('export_ribs', True)]

        scene_geoms = Wing3DExporter.build_scene_geoms(
            rib_data_to_export, other_meshes, is_left_wing=is_left, part_colors=part_colors
        )

        # リブ周長を計算（オフセットなし翻型輪郭）
        rib_perimeters_mm = []
        for pts in rib_orig_pts_list:
            diffs = np.diff(pts, axis=0)
            perim = float(np.sum(np.linalg.norm(diffs, axis=1)))
            perim += float(np.linalg.norm(pts[-1] - pts[0]))  # 閉じる
            rib_perimeters_mm.append(perim)

        # 主桦スパン長
        main_spar_mesh = scene_geoms.get('Main_Spar')
        if main_spar_mesh is not None and hasattr(main_spar_mesh, 'bounds'):
            b = main_spar_mesh.bounds
            ms_span_mm = float(b[1][1] - b[0][1])
        else:
            ms_span_mm = self.p.get('wing_span', 0.0) + self.p.get('joint_length', 0.0)

        analytics = {
            'rib_perimeters_mm': rib_perimeters_mm,
            'te_span_mm': te_span_mm,
            'main_spar_span_mm': ms_span_mm,
        }
        return scene_geoms, analytics

    def build_and_export(self, filepath):
        import trimesh
        scene_rib_data, other_meshes, part_colors, _rib_orig, _te_span = self._collect_geometry_data()
        is_left = self.p['wing_type'] == "Left"
        rib_data_to_export = [d for d in scene_rib_data if d[-1] != 'Ribs' or self.p.get('export_ribs', True)]
        Wing3DExporter.export_3d_scene(filepath, rib_data_to_export, other_meshes, is_left_wing=is_left, part_colors=part_colors)

    def _generate_rib_at_y(self, y_local, rib_index, thickness, is_carbon=False, te_cut_override=None):
        res = self.engine.generate_rib_at_y(self.p, y_local, rib_index, thickness, is_carbon, te_cut_override)
        y_global = y_local + self.p['joint_length']
        is_tip = (rib_index == len(self.p['y_positions']) - 1)
        y_ext = y_global + thickness if is_tip else y_global
        return res, res.c_m, y_ext

    def _generate_carbon_ribs_data(self, scene_rib_data):
        c_thick, t_rib = self.p['cr_thick'], self.p['rib_thick']
        for cconf in self.p['carbon_rib_configs']:
            if not cconf['act']: continue
            idx, y_local = cconf['idx'], self.p['y_positions'][cconf['idx']]
            y_global = y_local + self.p['joint_length']
            
            y_3d = y_global
            if cconf['loc'] == 'root': y_3d = y_global + t_rib if cconf['pos'] == 'inner' else y_global - c_thick
            elif cconf['loc'] == 'tip': y_3d = y_global - c_thick if cconf['pos'] == 'inner' else y_global + t_rib

            te_cut_override = self.p['te_cut'] if cconf['te'] else 0.0
            res, c_m, _ = self._generate_rib_at_y(y_local, idx, c_thick, is_carbon=True, te_cut_override=te_cut_override)
            
            rel_outline = self._to_rel(res[0], c_m)
            rel_holes = [self._to_rel(h, c_m) for h in [res[2], res[4], res[6], res[16], res[18]] + res[7] + res[8] + res[19] if len(h) > 0]
            scene_rib_data.append((y_3d, c_thick, rel_outline, rel_holes, 'CarbonRibs'))

    def _generate_connector_meshes(self, meshes, main_spar_centers, rear_spar_centers):
        if self.p['rear_spar_dia'] <= 0 or not self.p['connectors'] or len(rear_spar_centers) < 2: return
        p1_r, p2_r = np.array(rear_spar_centers[0]), np.array(rear_spar_centers[-1])
        R_main, r_conn = self.p['spar_hole_dia'] / 2.0, self.p['rear_spar_dia'] / 2.0

        # Construct solid representation of main and rear spars for boolean difference
        solid_main = Wing3DExporter.generate_swept_mesh(main_spar_centers, R_main)
        solid_rear = Wing3DExporter.generate_swept_mesh(rear_spar_centers, r_conn)
        sub_meshes = [m for m in [solid_main, solid_rear] if m is not None]

        for i, (y_c, conn_type) in enumerate(self.p['connectors']):
            if y_c is None or y_c == '': continue # パラメータが空の場合はスキップ
            
            if conn_type.startswith("V-Shape"):
                offset = r_conn
                # default to inner=up if just "V-Shape" (old saves)
                inner_goes_up = True if conn_type == "V-Shape" else ("In=Up" in conn_type or "In-up" in conn_type or "Out-down" in conn_type)
                
                y_inner = y_c - offset
                y_outer = y_c + offset
                
                y_up = y_inner if inner_goes_up else y_outer
                y_down = y_outer if inner_goes_up else y_inner
                
                # --- Upper Pipe ---
                t_up = (y_up - p1_r[1]) / (p2_r[1] - p1_r[1]) if p2_r[1] != p1_r[1] else 0
                p_rear_center_up = p1_r + t_up * (p2_r - p1_r)
                p_main_center_up = np.array([0.0, y_up, 0.0])
                
                vec_up = p_main_center_up - p_rear_center_up
                u_up = vec_up / np.linalg.norm(vec_up) if np.linalg.norm(vec_up) > 1e-5 else np.array([1,0,0])
                p_start_up = p_rear_center_up + u_up * r_conn
                p_end_upper = np.array([0.0, y_up, R_main - r_conn])
                
                # --- Lower Pipe ---
                t_down = (y_down - p1_r[1]) / (p2_r[1] - p1_r[1]) if p2_r[1] != p1_r[1] else 0
                p_rear_center_down = p1_r + t_down * (p2_r - p1_r)
                p_main_center_down = np.array([0.0, y_down, 0.0])
                
                vec_down = p_main_center_down - p_rear_center_down
                u_down = vec_down / np.linalg.norm(vec_down) if np.linalg.norm(vec_down) > 1e-5 else np.array([1,0,0])
                p_start_down = p_rear_center_down + u_down * r_conn
                p_end_lower = np.array([0.0, y_down, -R_main + r_conn])
                
                inner = self.p.get('rear_spar_inner_dia', r_conn*2 - 2.0) / 2.0
                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start_down, p_end_lower], r_conn, inner)
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_start_up, p_end_upper], r_conn, inner)
                
                if conn_lower and sub_meshes:
                    conn_lower = Wing3DExporter.blender_difference(conn_lower, sub_meshes)
                if conn_upper and sub_meshes:
                    conn_upper = Wing3DExporter.blender_difference(conn_upper, sub_meshes)
                    
                meshes[f"Connector_{i}_lower"] = conn_lower
                meshes[f"Connector_{i}_upper"] = conn_upper
                
            else:  # Y-Shape
                t = (y_c - p1_r[1]) / (p2_r[1] - p1_r[1]) if p2_r[1] != p1_r[1] else 0
                p_rear_center = p1_r + t * (p2_r - p1_r)
                
                p_main_center = np.array([0.0, y_c, 0.0])
                
                vec_to_main = p_main_center - p_rear_center
                u_to_main = vec_to_main / np.linalg.norm(vec_to_main) if np.linalg.norm(vec_to_main) > 1e-5 else np.array([1,0,0])

                # 始点：後縁スパーの中心から、コネクタ半径分だけ主桁側にオフセット
                p_start = p_rear_center + u_to_main * r_conn

                # 終点：主桁の中心から、コネクタ半径分だけ後縁スパー側にオフセット
                p_end_lower = np.array([0.0, y_c, -R_main + r_conn])
                p_end_upper = np.array([0.0, y_c, R_main - r_conn])
                
                # 1. リアスパーから主桁下面へのパイプ
                inner = self.p.get('rear_spar_inner_dia', r_conn*2 - 2.0) / 2.0
                conn_lower = Wing3DExporter.generate_pipe_mesh([p_start, p_end_lower], r_conn, inner)
                # 2. その中間点から主桁上面へのパイプ
                p_mid = (p_start + p_end_lower) / 2.0
                conn_upper = Wing3DExporter.generate_pipe_mesh([p_mid, p_end_upper], r_conn, inner)
                
                if conn_lower and sub_meshes:
                    conn_lower = Wing3DExporter.blender_difference(conn_lower, sub_meshes)
                if conn_upper and sub_meshes:
                    conn_upper = Wing3DExporter.blender_difference(conn_upper, sub_meshes)
                    
                meshes[f"Connector_{i}_lower"] = conn_lower
                meshes[f"Connector_{i}_upper"] = conn_upper

    def _generate_diag_spar_meshes(self, meshes, main_spar_centers, rear_spar_centers):
        if len(rear_spar_centers) < 2: return
        p1_r, p2_r = np.array(rear_spar_centers[0]), np.array(rear_spar_centers[-1])
        def get_rear_pt(y): return p1_r + ((y - p1_r[1]) / (p2_r[1] - p1_r[1]) if p2_r[1] != p1_r[1] else 0) * (p2_r - p1_r)

        R_main, r_rear = self.p['spar_hole_dia'] / 2.0, self.p['rear_spar_dia'] / 2.0
        
        # Construct solid representation of main and rear spars for boolean difference
        solid_main = Wing3DExporter.generate_swept_mesh(main_spar_centers, R_main)
        solid_rear = Wing3DExporter.generate_swept_mesh(rear_spar_centers, r_rear)
        sub_meshes = [m for m in [solid_main, solid_rear] if m is not None]

        for i, active, Y_m, Y_r, R_diag in [(1, self.p['diag1_active'], self.p['diag1_y_main'], self.p['diag1_y_rear'], self.p['rear_spar_dia']/2.0),
                                             (2, self.p['diag2_active'], self.p['diag2_y_main'], self.p['diag2_y_rear'], self.p['rear_spar_dia']/2.0)]:
            if not active: continue
            p_m, p_r = np.array([0.0, Y_m, 0.0]), get_rear_pt(Y_r)
            vec_xz = np.array([p_r[0] - p_m[0], 0.0, p_r[2] - p_m[2]])
            dist_xz = np.linalg.norm(vec_xz)
            if dist_xz > 1e-5:
                u_xz = vec_xz / dist_xz
                # 始点と終点を、各スパーの半径分だけ内側にオフセット
                p_start, p_end = p_m + u_xz * (R_main - R_diag), p_r - u_xz * (r_rear - R_diag)
                if np.linalg.norm(p_end - p_start) > 1e-5:
                    # Use diag1 or diag2 inner dia depending on the diag loop. We don't have the index easily here, so we use diag1 as default.
                    inner = self.p.get('rear_spar_inner_dia', R_diag*2 - 2.0) / 2.0
                    diag_mesh = Wing3DExporter.generate_pipe_mesh([p_start, p_end], R_diag, inner)
                    if diag_mesh and sub_meshes:
                        diag_mesh = Wing3DExporter.blender_difference(diag_mesh, sub_meshes)
                    meshes[f"Diag_Spar_{i}"] = diag_mesh

    def _generate_xbrace_meshes(self, meshes, rear_spar_centers):
        if not self.p['export_xbrace_wires'] or len(rear_spar_centers) < 2: return

        p1_r = np.array(rear_spar_centers[0])
        p2_r = np.array(rear_spar_centers[-1])
        def get_rear_pt(y_val):
            t = (y_val - p1_r[1]) / (p2_r[1] - p1_r[1]) if p2_r[1] != p1_r[1] else 0
            return p1_r + t * (p2_r - p1_r)

        R_main = self.p['spar_hole_dia'] / 2.0
        r_conn = self.p['rear_spar_dia'] / 2.0
        wire_radius = self.p.get('xbrace_wire_dia', 2.0) / 2.0  # ケブラー線の太さ
        wire_idx = 0
        main_wraps = set()
        conn_wraps = set()

        for y_s, y_e, offset in self.p['xb_zones']:
            if y_s is None or y_e is None: continue
            p_rear_s, p_rear_e = get_rear_pt(y_s), get_rear_pt(y_e)
            y_m_s, y_m_e = p_rear_s[1] - offset, p_rear_e[1] + offset

            vec_s = p_rear_s - np.array([0.0, y_m_s, 0.0])
            u_s = vec_s / np.linalg.norm(vec_s) if np.linalg.norm(vec_s) > 0 else np.array([1.0, 0.0, 0.0])
            vec_e = p_rear_e - np.array([0.0, y_m_e, 0.0])
            u_e = vec_e / np.linalg.norm(vec_e) if np.linalg.norm(vec_e) > 0 else np.array([1.0, 0.0, 0.0])

            c_wrap_s = p_rear_s - u_s * (r_conn * 2.0)
            c_wrap_e = p_rear_e - u_e * (r_conn * 2.0)

            for y_val in (y_m_s, y_m_e):
                if y_val not in main_wraps:
                    # 主桁巻き付け部をトーラス形状に変更
                    wrap_m = Wing3DExporter.generate_torus_mesh(center=[0.0, y_val, 0.0], major_radius=R_main, minor_radius=wire_radius)
                    if wrap_m: meshes[f"XBraceWire_WrapM_{wire_idx}"] = wrap_m
                    main_wraps.add(y_val); wire_idx += 1
            
            for y_c, c_wrap, u_vec in [(y_s, c_wrap_s, u_s), (y_e, c_wrap_e, u_e)]:
                if y_c not in conn_wraps:
                    is_v_shape = False
                    for cy, ctype in self.p['connectors']:
                        if cy is not None and abs(cy - y_c) < 1e-3 and ctype.startswith("V-Shape"):
                            is_v_shape = True
                            break
                    
                    if is_v_shape:
                        # V字コネクタの場合は2本のパイプを覆うようにY軸方向に長いスタジアム型のトーラスにする
                        wrap_c = Wing3DExporter.generate_stadium_torus_mesh(c_wrap, u_vec, r_conn, r_conn, wire_radius)
                    else:
                        # 通常のY字コネクタは従来通り
                        path_c = [c_wrap - u_vec * wire_radius, c_wrap + u_vec * wire_radius]
                        wrap_c = Wing3DExporter.generate_swept_mesh(path_c, r_conn + wire_radius)
                        
                    if wrap_c: meshes[f"XBraceWire_WrapC_{wire_idx}"] = wrap_c
                    conn_wraps.add(y_c); wire_idx += 1

            p_m1 = np.array([0.0, y_m_s, 0.0]) + u_s * (R_main + wire_radius)
            p_c1 = c_wrap_e + np.array([0.0, 0.0, r_conn + wire_radius])
            p_c2 = c_wrap_s + np.array([0.0, 0.0, -(r_conn + wire_radius)])
            p_m2 = np.array([0.0, y_m_e, 0.0]) + u_e * (R_main + wire_radius)
            
            meshes[f"XBraceWire_{wire_idx}"] = Wing3DExporter.generate_swept_mesh([p_m1, p_c1], wire_radius); wire_idx += 1
            meshes[f"XBraceWire_{wire_idx}"] = Wing3DExporter.generate_swept_mesh([p_c2, p_m2], wire_radius); wire_idx += 1

    def _generate_joint_sleeves(self, meshes):
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

            # helper to create and place annulus
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
                if foam_mesh: meshes[f"JointSleeve_Foam_{i}"] = foam_mesh

    def _to_rel(self, pts, c_m):
        return np.array(pts) - c_m if pts is not None and len(pts) > 0 else []


class Wing3DExporter:
    @staticmethod
    def build_scene_geoms(rib_data_list, other_meshes=None, is_left_wing=False, part_colors=None):
        """
        リブデータとother_meshesからジオメトリ辞書を構築して返す。
        ファイルへの書き出しは行わない。
        """

        try:
            import trimesh
            from shapely.geometry import Polygon
        except ImportError:
            raise ImportError("trimesh and shapely are required for 3D export.")

        if other_meshes is None: other_meshes = {}
        if part_colors is None:
            part_colors = {}
        meshes = []
        last_err = ""

        for data in rib_data_list:
            if len(data) == 4:
                y_global, thickness, ext_pts, holes = data
                mat_key = 'Ribs'
            else:
                y_global, thickness, ext_pts, holes, mat_key = data

            if len(ext_pts) < 3: continue
            try:
                poly = Polygon(ext_pts).buffer(0)
                for h in holes:
                    if len(h) >= 3:
                        hp = Polygon(h).buffer(0)
                        if poly.intersects(hp):
                            poly = poly.difference(hp).buffer(0)

                if poly.is_empty: continue
                polys_to_extrude = [poly] if getattr(poly, 'geom_type', '') == 'Polygon' else list(getattr(poly, 'geoms', []))

                for p in polys_to_extrude:
                    if p.is_empty or getattr(p, 'geom_type', '') != 'Polygon': continue
                    try:
                        p_simp = p.simplify(0.01, preserve_topology=True).buffer(0)
                        if getattr(p_simp, 'geom_type', '') != 'Polygon': p_simp = p

                        mesh = trimesh.creation.extrude_polygon(p_simp, height=thickness)
                        swap_yz = np.array([
                            [1, 0, 0, 0],
                            [0, 0, 1, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1]
                        ])
                        mesh.apply_transform(swap_yz)
                        mesh.apply_translation([0, y_global, 0])
                        meshes.append((mesh, mat_key))
                    except Exception as e: last_err = str(e); print("Extrude Error:", e)
            except Exception as e: last_err = str(e); print("Extrude Error:", e)

        scene_geoms = {}

        try:
            from trimesh.visual.material import PBRMaterial
        except ImportError:
            PBRMaterial = None

        def apply_color(mesh_obj, color_props):
            if isinstance(color_props, tuple) and len(color_props) == 3:
                color_rgba, metallic, roughness = color_props
            else:
                color_rgba, metallic, roughness = color_props, 0.1, 0.5

            mesh_obj.visual.face_colors = color_rgba
            if PBRMaterial:
                a_mode = 'BLEND' if color_rgba[3] < 255 else 'OPAQUE'
                mesh_obj.visual.material = PBRMaterial(baseColorFactor=color_rgba, metallicFactor=metallic, roughnessFactor=roughness, doubleSided=True, alphaMode=a_mode)

        ribs_m_list = [m for m, k in meshes if k == 'Ribs']
        if ribs_m_list:
            ribs_mesh = trimesh.util.concatenate(ribs_m_list)
            c = part_colors.get('Ribs', ([200, 200, 200, 255], 0.1, 0.5))
            apply_color(ribs_mesh, c)
            scene_geoms['Ribs'] = ribs_mesh

        carbon_m_list = [m for m, k in meshes if k == 'CarbonRibs']
        if carbon_m_list:
            cr_mesh = trimesh.util.concatenate(carbon_m_list)
            c = part_colors.get('CarbonRibs', ([30, 30, 30, 255], 0.2, 0.1))
            apply_color(cr_mesh, c)
            scene_geoms['CarbonRibs'] = cr_mesh

        rc_m_list = [m for m, k in meshes if k == 'Rib_Cap']
        if rc_m_list:
            rc_mesh = trimesh.util.concatenate(rc_m_list)
            c = part_colors.get('Rib_Cap', ([30, 30, 30, 255], 0.2, 0.1))
            apply_color(rc_mesh, c)
            scene_geoms['Rib_Cap'] = rc_mesh

        rib_sub_meshes = ribs_m_list + carbon_m_list
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
                                s_mat[0, 0] = 1.02  # 少し前後に伸ばして薄皮を防ぐ
                                s_mat[1, 1] = scale # 幅を広げる
                                s_mat[2, 2] = 1.02  # 少し上下に伸ばして薄皮を防ぐ
                                
                                t2 = np.eye(4)
                                t2[0, 3] = x_center
                                t2[1, 3] = y_center
                                t2[2, 3] = z_center
                                
                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                            extended_subs.append(sub_ext)
                        except Exception as e:
                            print("Scaling sub error:", e)
                            extended_subs.append(sub)
                    m = Wing3DExporter.blender_difference(m, extended_subs)
                c = [200, 200, 200, 255]
                for k, v in part_colors.items():
                    if name.startswith(k):
                        c = v
                        break
                apply_color(m, c)
                scene_geoms[name] = m

        if not scene_geoms:
            msg = "No valid 3D meshes could be generated."
            if last_err: msg += f"\nLast Error: {last_err}"
            raise ValueError(msg)

        # 左羼の場合は、Y軸（スパン方向）を反転させて左右対称にする
        if is_left_wing:
            mirror_mat = np.eye(4)
            mirror_mat[1, 1] = -1
            for m in scene_geoms.values():
                m.apply_transform(mirror_mat)
                m.faces = np.fliplr(m.faces)

        return scene_geoms

    @staticmethod
    def export_3d_scene(filepath, rib_data_list, other_meshes=None, is_left_wing=False, part_colors=None):
        """build_scene_geomsでジオメトリを構築したのちファイルに書き出す"""
        import trimesh
        import os
        import numpy as np
        scene_geoms = Wing3DExporter.build_scene_geoms(
            rib_data_list, other_meshes, is_left_wing=is_left_wing, part_colors=part_colors
        )
        scene = trimesh.Scene(geometry=scene_geoms)

        # GLTF/GLB formats strictly require units in meters. Since Ribgenerator uses mm,
        # we scale the scene by 0.001 to convert mm to meters before exporting to glb.
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.glb', '.gltf']:
            scale_matrix = np.eye(4)
            scale_matrix[0, 0] = 0.001
            scale_matrix[1, 1] = 0.001
            scale_matrix[2, 2] = 0.001
            scene.apply_transform(scale_matrix)

        scene.export(filepath)

    @staticmethod
    def generate_swept_mesh(points_3d, radius, sections=16):
        if len(points_3d) < 2 or radius <= 0: return None
        try:
            import trimesh
            
            p1 = np.array(points_3d[0])
            p2 = np.array(points_3d[-1])
            vec = p2 - p1
            dist = np.linalg.norm(vec)
            if dist < 1e-6: return None
            
            # 環境によるエラーを防ぐため、手動で回転させて円柱を配置します
            mesh = trimesh.creation.cylinder(radius=radius, height=dist, sections=sections)
            rot = trimesh.geometry.align_vectors([0, 0, 1], vec / dist)
            rot[:3, 3] = (p1 + p2) / 2.0
            mesh.apply_transform(rot)
            return mesh
        except Exception as e:
            print("Swept Mesh Error:", e)
            return None

    @staticmethod
    def generate_pipe_mesh(points_3d, outer_radius, inner_radius, sections=32):
        """
        指定された3D点の経路に沿って、端が閉じていない中空のパイプメッシュを生成します。
        ブーリアン演算を使用せずに、頂点と面から直接メッシュを構築します。
        """
        rx_out, ry_out = outer_radius if isinstance(outer_radius, tuple) else (outer_radius, outer_radius)
        rx_in, ry_in = inner_radius if isinstance(inner_radius, tuple) else (inner_radius, inner_radius)
        
        if len(points_3d) < 2 or rx_out <= rx_in or ry_out <= ry_in or rx_in < 0 or ry_in < 0:
            return None
        try:
            import trimesh
            vertices = []
            
            # パイプの各セクションの頂点を生成
            for i in range(len(points_3d)):
                p1 = np.array(points_3d[i])
                # パイプの方向ベクトルを計算
                if i < len(points_3d) - 1:
                    direction = np.array(points_3d[i+1]) - p1
                else: # 最後の点
                    direction = p1 - np.array(points_3d[i-1])

                if np.linalg.norm(direction) < 1e-6:
                    direction = np.array([0, 1, 0]) # デフォルト方向

                # 断面を定義するための基底ベクトルを計算
                v_ref = np.array([0, 0, 1]) if np.abs(np.dot(direction / np.linalg.norm(direction), [0,0,1])) < 0.9 else np.array([0, 1, 0])
                u = np.cross(direction, v_ref)
                u /= np.linalg.norm(u)
                v = np.cross(direction, u)
                v /= np.linalg.norm(v)

                # 円周上の頂点を計算
                for j in range(sections):
                    angle = 2 * np.pi * j / sections
                    # 外側と内側の頂点を追加
                    vertices.append(p1 + rx_out * np.cos(angle) * u + ry_out * np.sin(angle) * v)
                    vertices.append(p1 + rx_in * np.cos(angle) * u + ry_in * np.sin(angle) * v)

            faces = []
            # パイプの側面（外側と内側）の面を生成
            for i in range(len(points_3d) - 1):
                for j in range(sections):
                    p_idx = (i * sections + j) * 2
                    p_next_idx = (i * sections + (j + 1) % sections) * 2
                    s_idx = ((i + 1) * sections + j) * 2
                    s_next_idx = ((i + 1) * sections + (j + 1) % sections) * 2

                    # 外側の面
                    faces.append([p_idx, s_idx, p_next_idx])
                    faces.append([p_next_idx, s_idx, s_next_idx])
                    # 内側の面（法線が内側を向くように順序を逆にする）
                    faces.append([p_idx + 1, p_next_idx + 1, s_idx + 1])
                    faces.append([p_next_idx + 1, s_next_idx + 1, s_idx + 1])

            # パイプの端に円環状のメッシュを追加して蓋をする
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
                faces.append([p_next_idx, p_idx + 1, p_next_idx + 1])

            return trimesh.Trimesh(vertices=vertices, faces=faces)
        except Exception as e:
            print(f"Pipe Mesh Error: {e}")
            return None

    @staticmethod
    def generate_torus_mesh(center, major_radius, minor_radius, major_sections=32, minor_sections=16):
        """指定された中心と半径でトーラスメッシュを生成する。"""
        try:
            import trimesh
            torus = trimesh.creation.torus(
                major_radius=major_radius,
                minor_radius=minor_radius,
                major_sections=major_sections,
                minor_sections=minor_sections
            )
            # Y軸周りに90度回転させて、XY平面に平行なトーラスにする
            rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
            torus.apply_transform(rot)
            torus.apply_translation(center)
            return torus
        except Exception as e:
            print(f"Torus Mesh Error: {e}")
            return None

    @staticmethod
    def generate_stadium_torus_mesh(center, normal_vec, offset_y, r_pipe, wire_radius, num_pts=16):
        """
        指定された方向(normal_vec)に法線を持つスタジアム型（または円形）のトーラスを生成する。
        offset_y=0 の場合は円形トーラスになる。
        """
        try:
            import trimesh
            import shapely.geometry as sg
            
            circle = sg.Point(0, 0).buffer(wire_radius)
            r_path = r_pipe + wire_radius
            
            path_pts = []
            # Right semicircle
            for i in range(num_pts + 1):
                angle = -np.pi/2 + np.pi * i / num_pts
                path_pts.append([0.0, offset_y + r_path * np.cos(angle), r_path * np.sin(angle)])
                
            # Left semicircle
            for i in range(num_pts + 1):
                angle = np.pi/2 + np.pi * i / num_pts
                path_pts.append([0.0, -offset_y + r_path * np.cos(angle), r_path * np.sin(angle)])
                
            path_pts.append(path_pts[0])
            path = np.array(path_pts)
            
            mesh = trimesh.creation.sweep_polygon(circle, path)
            
            # normal_vecに合うように回転（デフォルトの法線はX軸 [1, 0, 0]）
            n_vec = np.array(normal_vec)
            if np.linalg.norm(n_vec) > 1e-6:
                n_vec = n_vec / np.linalg.norm(n_vec)
                rot = trimesh.geometry.align_vectors([1, 0, 0], n_vec)
                mesh.apply_transform(rot)
                
            mesh.apply_translation(center)
            return mesh
        except Exception as e:
            print(f"Stadium Torus Mesh Error: {e}")
            return None

    @staticmethod
    def generate_lofted_surface(curves_3d):
        if len(curves_3d) < 2: return None
        try:
            import trimesh
            from shapely.geometry import Polygon
            
            valid_curves = [c for c in curves_3d if len(c) >= 3]
            if len(valid_curves) < 2: return None

            # Ensure all curves are closed beforehand to determine true max_len
            for i in range(len(valid_curves)):
                if np.linalg.norm(valid_curves[i][0] - valid_curves[i][-1]) > 1e-5:
                    valid_curves[i] = np.vstack([valid_curves[i], valid_curves[i][0]])
                    
            max_len = max(len(c) for c in valid_curves)

            def resample_closed(curve, n):
                dist = np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))
                dist = np.insert(dist, 0, 0)
                if dist[-1] == 0: return np.tile(curve[0], (n, 1))
                target = np.linspace(0, dist[-1], n)
                corners = []
                for i in range(1, len(curve)-1):
                    v1 = curve[i] - curve[i-1]
                    v2 = curve[i+1] - curve[i]
                    n1 = np.linalg.norm(v1)
                    n2 = np.linalg.norm(v2)
                    if n1 > 1e-5 and n2 > 1e-5:
                        cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
                        if np.arccos(cos_th) > 0.5:
                            corners.append(dist[i])
                
                for c_dist in corners:
                    idx = np.argmin(np.abs(target - c_dist))
                    if idx == 0 or idx == n - 1: continue
                    if c_dist <= target[idx-1]: continue
                    if c_dist >= target[idx+1]: continue
                    target[idx] = c_dist
                    
                return np.array([np.interp(target, dist, curve[:, i]) for i in range(3)]).T
                
            all_same_len = all(len(c) == max_len for c in valid_curves)
            
            aligned_curves = []
            for i, c in enumerate(valid_curves):
                if all_same_len and max_len <= 10:
                    c_res = c
                else:
                    c_res = resample_closed(c, max_len)
                    
                if np.linalg.norm(c_res[0] - c_res[-1]) > 1e-5:
                    c_res = np.vstack([c_res, c_res[0]])
                    
                if i > 0:
                    prev_c = aligned_curves[-1]
                    min_dist_sum = float('inf')
                    best_roll = 0
                    for j in range(len(c_res)-1):
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll = dist_sum, j
                    shifted_core = np.roll(c_res[:-1], -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])
                    
                aligned_curves.append(c_res)
                
            vertices = np.vstack(aligned_curves)
            faces = []
            pts_per_curve = len(aligned_curves[0])
            
            for i in range(len(aligned_curves) - 1):
                offset1 = i * pts_per_curve
                offset2 = (i + 1) * pts_per_curve
                for j in range(pts_per_curve - 1):
                    p1 = offset1 + j
                    p2 = offset1 + j + 1
                    p3 = offset2 + j
                    p4 = offset2 + j + 1
                    faces.append([p1, p2, p3])
                    faces.append([p3, p2, p4])
                
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # 両端に蓋をする
            def make_cap(curve_3d, flip_normal=False):
                poly_2d = Polygon(curve_3d[:, [0, 2]]).buffer(0)
                if poly_2d.is_empty: return None
                try:
                    v, f = trimesh.creation.triangulate_polygon(poly_2d)
                    v_3d = np.zeros((len(v), 3))
                    v_3d[:, 0] = v[:, 0]
                    v_3d[:, 1] = curve_3d[0, 1]
                    v_3d[:, 2] = v[:, 1]
                    if flip_normal: f = np.fliplr(f)
                    return trimesh.Trimesh(vertices=v_3d, faces=f)
                except:
                    return None

            cap1 = make_cap(aligned_curves[0], flip_normal=True)
            cap2 = make_cap(aligned_curves[-1], flip_normal=False)
            
            meshes = [mesh]
            if cap1: meshes.append(cap1)
            if cap2: meshes.append(cap2)
            
            final_mesh = trimesh.util.concatenate(meshes)
            try:
                final_mesh.merge_vertices()
                final_mesh.remove_unreferenced_vertices()
            except:
                pass
            try:
                if final_mesh.volume < 0:
                    final_mesh.faces = np.fliplr(final_mesh.faces)
            except:
                pass
            return final_mesh
        except Exception as e:
            print("Lofted Surface Error:", e)
            return None

    @staticmethod
    def blender_difference(base_mesh, subtract_meshes):
        """
        Performs a boolean difference using Blender: base_mesh - union(subtract_meshes)
        """
        import tempfile
        import subprocess
        import trimesh
        import os
        
        if not base_mesh or len(base_mesh.vertices) == 0:
            return base_mesh
            
        valid_subtract = [m for m in subtract_meshes if m is not None and len(m.vertices) > 0]
        if not valid_subtract:
            return base_mesh
            
        try:
            base_mesh.merge_vertices()
            base_mesh.remove_unreferenced_vertices()
            if base_mesh.volume < 0:
                base_mesh.faces = np.fliplr(base_mesh.faces)
        except:
            pass

        for m in valid_subtract:
            try:
                m.merge_vertices()
                m.remove_unreferenced_vertices()
                if m.volume < 0:
                    m.faces = np.fliplr(m.faces)
            except:
                pass

        temp_dir = tempfile.gettempdir()
        base_path = os.path.join(temp_dir, f"base_{id(base_mesh)}.stl")
        sub_paths = []
        
        try:
            base_mesh.export(base_path)
            for idx, m in enumerate(valid_subtract):
                p = os.path.join(temp_dir, f"sub_{id(base_mesh)}_{idx}.stl")
                m.export(p)
                sub_paths.append(p)
                
            out_path = os.path.join(temp_dir, f"out_{id(base_mesh)}.stl")
            if os.path.exists(out_path):
                os.remove(out_path)
                
            # Write Python script for Blender
            script_lines = [
                "import bpy",
                "import os",
                "bpy.ops.object.select_all(action='SELECT')",
                "bpy.ops.object.delete(use_global=True)",
                f"bpy.ops.wm.stl_import(filepath={repr(base_path)})",
            ]
            for p in sub_paths:
                script_lines.append(f"bpy.ops.wm.stl_import(filepath={repr(p)})")
                
            script_lines.extend([
                "bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True)",
                "base_obj = bpy.data.objects[0]",
                "bpy.ops.object.select_all(action='DESELECT')",
                "base_obj.select_set(True)",
                "bpy.context.view_layer.objects.active = base_obj",
                "bpy.ops.object.mode_set(mode='EDIT')",
                "bpy.ops.mesh.select_all(action='SELECT')",
                "bpy.ops.mesh.remove_doubles()",
                "bpy.ops.object.mode_set(mode='OBJECT')",
                "if len(bpy.data.objects) > 1:",
                "    bpy.ops.object.select_all(action='DESELECT')",
                "    for other in bpy.data.objects[1:]:",
                "        other.select_set(True)",
                "    bpy.context.view_layer.objects.active = bpy.data.objects[1]",
                "    bpy.ops.object.join()",
                "    joined_sub = bpy.context.view_layer.objects.active",
                "    bpy.ops.object.mode_set(mode='EDIT')",
                "    bpy.ops.mesh.select_all(action='SELECT')",
                "    bpy.ops.mesh.remove_doubles()",
                "    bpy.ops.object.mode_set(mode='OBJECT')",
                "    bpy.ops.object.select_all(action='DESELECT')",
                "    base_obj.select_set(True)",
                "    bpy.context.view_layer.objects.active = base_obj",
                "    mod = base_obj.modifiers.new('bool_joined', 'BOOLEAN')",
                "    mod.object = joined_sub",
                "    mod.operation = 'DIFFERENCE'",
                "    mod.solver = 'EXACT'",
                "    bpy.ops.object.modifier_apply(modifier=mod.name)",
                "    bpy.ops.object.select_all(action='DESELECT')",
                "    joined_sub.select_set(True)",
                "    bpy.ops.object.delete()",
                "bpy.ops.object.select_all(action='DESELECT')",
                "base_obj.select_set(True)",
                "bpy.context.view_layer.objects.active = base_obj",
                "bpy.ops.object.mode_set(mode='EDIT')",
                "bpy.ops.mesh.select_all(action='SELECT')",
                "bpy.ops.mesh.normals_make_consistent(inside=False)",
                "bpy.ops.object.mode_set(mode='OBJECT')",
                f"bpy.ops.export_mesh.stl(filepath={repr(out_path)}, use_selection=True)"
            ])
            
            script_path = os.path.join(temp_dir, f"run_bool_{id(base_mesh)}.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("\n".join(script_lines))
                
            # Run blender in background
            subprocess.run(["blender", "--background", "--python", script_path], capture_output=True, check=True)
            if os.path.exists(out_path):
                result = trimesh.load(out_path)
                if isinstance(result, trimesh.Scene):
                    if len(result.geometry) > 0:
                        result = trimesh.util.concatenate(list(result.geometry.values()))
                    else:
                        result = trimesh.Trimesh()
                try:
                    result.merge_vertices()
                    result.remove_unreferenced_vertices()
                except:
                    pass
                return result
            else:
                return base_mesh
        except Exception as e:
            print("Blender Boolean Error:", e)
            return base_mesh
        finally:
            # Clean up temp files
            for p in [base_path, out_path] + sub_paths:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
            script_p = os.path.join(temp_dir, f"run_bool_{id(base_mesh)}.py")
            if os.path.exists(script_p):
                try:
                    os.remove(script_p)
                except:
                    pass