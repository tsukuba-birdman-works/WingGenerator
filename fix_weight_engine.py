import re

with open('core/weight_engine.py', 'r') as f:
    text = f.read()

# Modify signature
old_sig = """    def calculate_weights(
        self,
        geometries: Dict[str, Any],
        mat_props: Dict,
        extra_analytics: Optional[Dict] = None,
    ) -> List[Dict]:"""
new_sig = """    def calculate_weights(
        self,
        geometries: Dict[str, Any],
        mat_props: Dict,
        extra_analytics: Optional[Dict] = None,
        wing_params: Optional[Dict] = None,
    ) -> List[Dict]:"""
text = text.replace(old_sig, new_sig)
if wing_params_fallback := "        wing_params = wing_params or {}":
    text = text.replace("        mesh_props = self.compute_mesh_properties(geometries)",
                        "        wing_params = wing_params or {}\n        mesh_props = self.compute_mesh_properties(geometries)")

# Rewrite Rear Spar
old_rear = """        # Rear Spar: 体積×体積密度
        if 'rear_spar' in category_data:
            d = category_data['rear_spar']
            w = d['volume_cm3'] * rho_ct
            results.append(_row('Rear_Spar', 'rear_spar', '後桁 (Rear Spar)',
                                f"V={d['volume_cm3']:.2f}cm³",
                                w, 'V×ρ_carbon_tube'))"""
new_rear = """        # Rear Spar: 解析的計算 (Length × CrossArea × Density)
        if 'rear_spar' in category_data:
            d = category_data['rear_spar']
            span_m = d['bbox_span_m']
            od = wing_params.get('rear_spar_dia', 0.0)
            t = wing_params.get('rear_spar_thickness', 0.0) # Assumed thickness param if exists
            if t <= 0: t = 1.0 # Default 1mm thickness
            id_ = max(0.0, od - 2*t)
            area_cm2 = (np.pi/4) * (od**2 - id_**2) / 100.0
            w = (span_m * 100.0) * area_cm2 * rho_ct
            results.append(_row('Rear_Spar', 'rear_spar', '後桁 (Rear Spar)',
                                f"L={span_m*1000:.1f}mm, OD={od}mm, t={t}mm",
                                w, '解析的計算(円筒) × ρ'))"""
text = text.replace(old_rear, new_rear)

# Rewrite Main Spar
old_main = """        # Main Spar: 固定重量 or 長さ×線密度
        main_spar_mode = mat_props.get('main_spar_mode', 'weight')
        if True:  # 主桁は常に出力
            if main_spar_mode == 'weight':
                w = mat_props.get('main_spar_weight_g', 0.0)
                qty_str = f"{w:.2f} g (固定入力)"
                note = '固定重量入力'
            else:
                lam_ms = mat_props.get('main_spar_linear_density', 100.0)
                # extra_analytics から主桁スパン長を取得（Wing3DBuilder.build_geometry が返す値）
                if extra_analytics and 'main_spar_span_mm' in extra_analytics:
                    span_m = extra_analytics['main_spar_span_mm'] / 1000.0
                elif 'main_spar' in category_data:
                    span_m = category_data['main_spar']['bbox_span_m']
                else:
                    span_m = 0.0
                w = span_m * lam_ms
                qty_str = f"L={span_m*1000:.1f}mm × {lam_ms:.2f}g/m"
                note = 'L × 線密度'
            results.append(_row('Main_Spar', 'main_spar', '主桁 (Main Spar)', qty_str, w, note))"""

new_main = """        # Main Spar: 解析的計算
        main_spar_mode = mat_props.get('main_spar_mode', 'weight')
        if True:
            if main_spar_mode == 'weight':
                w = mat_props.get('main_spar_weight_g', 0.0)
                results.append(_row('Main_Spar', 'main_spar', '主桁 (Main Spar)', f"{w:.2f} g", w, '固定重量'))
            else:
                span_m = extra_analytics.get('main_spar_span_mm', 0.0)/1000.0 if extra_analytics else 0.0
                if span_m == 0 and 'main_spar' in category_data: span_m = category_data['main_spar']['bbox_span_m']
                od = wing_params.get('main_spar_dia', 0.0)
                t = wing_params.get('main_spar_thickness', 0.0)
                if t <= 0: t = 1.0
                id_ = max(0.0, od - 2*t)
                area_cm2 = (np.pi/4) * (od**2 - id_**2) / 100.0
                w = (span_m * 100.0) * area_cm2 * rho_ct
                results.append(_row('Main_Spar', 'main_spar', '主桁 (Main Spar)', f"L={span_m*1000:.1f}mm, OD={od}mm", w, '解析的計算(円筒) × ρ'))"""
text = text.replace(old_main, new_main)


# Rewrite Stringers
old_str = """        # Stringers: 体積×体積密度
        if 'stringer' in category_data:
            d = category_data['stringer']
            w = d['volume_cm3'] * rho_str
            results.append(_row('Stringers', 'stringer', 'ストリンガー',
                                f"V={d['volume_cm3']:.2f}cm³",
                                w, 'V×ρ_stringer'))"""
new_str = """        # Stringers: 解析的計算
        if 'stringer' in category_data:
            d = category_data['stringer']
            span_m = d['bbox_span_m']
            s_data = wing_params.get('stringers_data', [])
            total_area_mm2 = sum(s.get('width', 0) * s.get('depth', 0) for s in s_data)
            area_cm2 = total_area_mm2 / 100.0
            w = (span_m * 100.0) * area_cm2 * rho_str
            results.append(_row('Stringers', 'stringer', 'ストリンガー',
                                f"L≈{span_m*1000:.1f}mm, Area={total_area_mm2:.1f}mm²",
                                w, '解析的計算(断面×長) × ρ'))"""
text = text.replace(old_str, new_str)

# Rewrite Diagonals
old_diag = """        # Diagonal Spars: 体積×体積密度
        if 'diag_spar' in category_data:
            d = category_data['diag_spar']
            w = d['volume_cm3'] * rho_ct
            results.append(_row('Diag_Spars', 'diag_spar', '斜めスパー',
                                f"V={d['volume_cm3']:.2f}cm³",
                                w, 'V×ρ_carbon_tube'))"""
new_diag = """        # Diagonal Spars: 解析的計算 (bbox is inaccurate for diagonals, but we'll use sum of actual lengths if available, else fallback)
        if 'diag_spar' in category_data:
            d = category_data['diag_spar']
            vol_cm3 = d['volume_cm3']
            # If we don't have exact lengths from params, use mesh volume as fallback or approximate length
            w = vol_cm3 * rho_ct
            od = wing_params.get('diag_spar_dia', 0.0)
            results.append(_row('Diag_Spars', 'diag_spar', '斜めスパー',
                                f"V={vol_cm3:.2f}cm³ (OD={od}mm)",
                                w, 'メッシュ体積 × ρ (傾斜のため)'))"""
text = text.replace(old_diag, new_diag)

with open('core/weight_engine.py', 'w') as f:
    f.write(text)

