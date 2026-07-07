"""
重量計算エンジン
各パーツの体積・面積・長さを元に重量を計算する
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple


# ==========================================
# デフォルト物性値
# ==========================================
DEFAULT_MATERIAL_PROPS = {
    # フォーム材
    'foam_volume_density':    0.030,  # g/cm³  (スタイロフォーム)
    'foam_skin_area_density': 50.0,   # g/m²   (溶融スキン)

    # 主桁（どちらかのモードで使用）
    'main_spar_mode':         'weight',   # 'weight' or 'linear_density'
    'main_spar_weight_g':     0.0,        # g  （固定重量モード）
    'main_spar_linear_density': 100.0,   # g/m （線密度モード）

    # カーボンパイプ系 (後桁・コネクタ・斜めスパー)
    'carbon_tube_volume_density': 1.6,   # g/cm³

    # ストリンガー
    'stringer_volume_density': 0.50,     # g/cm³ （バルサ等）

    # Xブレースワイヤー
    'xbrace_linear_density':  1.5,       # g/m  （ケブラー等）

    # カーボンリブ（薄板）
    'carbon_rib_area_density':  200.0,   # g/m²
    'carbon_rib_adhesive_density': 20.0, # g/m² （接着剤）

    # カーボンキャップ（TE Cap / Rib Cap）
    'carbon_cap_area_density':  200.0,   # g/m²
    'carbon_cap_adhesive_density': 20.0, # g/m²

    # OPPフィルム
    'film_area_density': 20.0,           # g/m²

    # 両面テープ（3D非描画・解析的計算）
    'tape_linear_density': 5.0,          # g/m
}

# パーツ名プレフィックス → カテゴリ のマッピング
PART_CATEGORY = {
    'Ribs':         'ribs',
    'TE_Skin':      'te_skin',
    'Plank_Skin':   'plank_skin',
    'Main_Spar':    'main_spar',
    'Front_Spar':   'front_spar',
    'Rear_Spar':    'rear_spar',
    'Stringer_':    'stringer',
    'Connector_':   'connector',
    'Diag_Spar_':   'diag_spar',
    'XBraceWire_':  'xbrace',
    'CarbonRibs':   'carbon_ribs',
    'TE_Cap_':      'te_cap',
    'Rib_Cap':      'rib_cap',
    'Film_Skin':    'film',
}


def classify_part(name: str) -> str:
    """パーツ名からカテゴリに分類する"""
    for prefix, category in PART_CATEGORY.items():
        if name.startswith(prefix):
            return category
    return 'unknown'


class WeightCalculator:
    """
    GLBメッシュと物性値から各パーツの重量を計算するクラス。
    """

    def compute_mesh_properties(self, geometries: Dict[str, Any]) -> Dict[str, Dict]:
        """
        trimeshジオメトリ辞書から各パーツの体積・面積・長さを算出する。
        戻り値:
            {part_name: {'volume_cm3', 'area_m2', 'length_m', 'bbox_span_m'}}
        """
        props = {}
        for name, mesh in geometries.items():
            try:
                # trimesh.Trimesh を想定
                # ブーリアン演算後のメッシュは法線逆転で volume が負になる場合があるため abs() を使用
                vol_mm3 = abs(float(mesh.volume)) if hasattr(mesh, 'volume') else 0.0
                area_mm2 = float(mesh.area) if hasattr(mesh, 'area') else 0.0

                # バウンディングボックスのY軸スパン（スパー類の長さ推定用）
                bounds = mesh.bounds  # shape (2, 3)
                span_mm = float(bounds[1][1] - bounds[0][1]) if bounds is not None else 0.0

                props[name] = {
                    'volume_cm3':   vol_mm3 / 1000.0,  # mm³ → cm³
                    'area_m2':      area_mm2 / 1.0e6,   # mm² → m²
                    'bbox_span_m':  span_mm / 1000.0,   # mm → m
                }
            except Exception as e:
                props[name] = {'volume_cm3': 0.0, 'area_m2': 0.0, 'bbox_span_m': 0.0, 'error': str(e)}
        return props


    def calculate_weights(
        self,
        geometries: Dict[str, Any],
        mat_props: Dict,
        extra_analytics: Optional[Dict] = None,
        wing_params: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        メッシュプロパティと物性値から重量リストを生成する。

        Parameters
        ----------
        geometries : {name: trimesh.Trimesh}
        mat_props  : 物性値辞書（DEFAULT_MATERIAL_PROPS 参照）
        extra_analytics : {
            'rib_perimeters_mm': List[float],  # 各リブの翼型周長 [mm]
            'te_span_mm': float,               # 後縁スパン長 [mm]
        }

        Returns
        -------
        List of {
            'name', 'category', 'display_name',
            'quantity', 'unit', 'weight_g', 'note'
        }
        """
        wing_params = wing_params or {}
        mesh_props = self.compute_mesh_properties(geometries)
        results = []

        # --- メッシュベースの計算 ---
        # 集約するためのカテゴリ別バケット
        category_data = {}
        for name, mp in mesh_props.items():
            cat = classify_part(name)
            if cat not in category_data:
                category_data[cat] = {
                    'names': [], 'volume_cm3': 0.0, 'area_m2': 0.0, 'bbox_span_m': 0.0
                }
            category_data[cat]['names'].append(name)
            category_data[cat]['volume_cm3'] += mp['volume_cm3']
            category_data[cat]['area_m2'] += mp['area_m2']
            category_data[cat]['bbox_span_m'] += mp['bbox_span_m']

        rho_foam = mat_props.get('foam_volume_density', 0.030)
        sigma_skin = mat_props.get('foam_skin_area_density', 50.0)
        rho_ct = mat_props.get('carbon_tube_volume_density', 1.6)
        rho_str = mat_props.get('stringer_volume_density', 0.5)
        lam_xb = mat_props.get('xbrace_linear_density', 1.5)
        sigma_cr = mat_props.get('carbon_rib_area_density', 200.0)
        sigma_cr_adh = mat_props.get('carbon_rib_adhesive_density', 20.0)
        sigma_cap = mat_props.get('carbon_cap_area_density', 200.0)
        sigma_cap_adh = mat_props.get('carbon_cap_adhesive_density', 20.0)
        sigma_film = mat_props.get('film_area_density', 20.0)

        # Ribs: 体積×体積密度 + 表面積×溶融スキン面密度
        if 'ribs' in category_data:
            d = category_data['ribs']
            w = d['volume_cm3'] * rho_foam + d['area_m2'] * sigma_skin
            results.append(_row('Ribs', 'ribs', 'リブ (Foam + Skin)',
                                f"V={d['volume_cm3']:.2f}cm³, A={d['area_m2']*1e4:.1f}cm²",
                                w, 'V×ρ + A×σ_skin'))

        # TE_Skin: 体積×体積密度 + 表面積×溶融スキン面密度
        if 'te_skin' in category_data:
            d = category_data['te_skin']
            w = d['volume_cm3'] * rho_foam + d['area_m2'] * sigma_skin
            results.append(_row('TE_Skin', 'te_skin', '後縁材 (Foam + Skin)',
                                f"V={d['volume_cm3']:.2f}cm³, A={d['area_m2']*1e4:.1f}cm²",
                                w, 'V×ρ + A×σ_skin'))

        # Plank_Skin: 体積×体積密度 + 表面積×溶融スキン面密度
        if 'plank_skin' in category_data:
            d = category_data['plank_skin']
            w = d['volume_cm3'] * rho_foam + d['area_m2'] * sigma_skin
            results.append(_row('Plank_Skin', 'plank_skin', 'プランク (Foam + Skin)',
                                f"V={d['volume_cm3']:.2f}cm³, A={d['area_m2']*1e4:.1f}cm²",
                                w, 'V×ρ + A×σ_skin'))

        # Main Spar: 解析的計算
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
                results.append(_row('Main_Spar', 'main_spar', '主桁 (Main Spar)', f"L={span_m*1000:.1f}mm, OD={od}mm", w, '解析的計算(円筒) × ρ'))

        # Front Spar: 0g
        results.append(_row('Front_Spar', 'front_spar', '前桁 (Front Spar)',
                            '0g（計算対象外）', 0.0, '固定0g'))

        # Rear Spar: 解析的計算 (Length × CrossArea × Density)
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
                                w, '解析的計算(円筒) × ρ'))

        # Connectors: 体積×体積密度
        if 'connector' in category_data:
            d = category_data['connector']
            w = d['volume_cm3'] * rho_ct
            results.append(_row('Connectors', 'connector', 'コネクタ',
                                f"V={d['volume_cm3']:.2f}cm³",
                                w, 'V×ρ_carbon_tube'))

        # Diagonal Spars: 解析的計算 (bbox is inaccurate for diagonals, but we'll use sum of actual lengths if available, else fallback)
        if 'diag_spar' in category_data:
            d = category_data['diag_spar']
            vol_cm3 = d['volume_cm3']
            # If we don't have exact lengths from params, use mesh volume as fallback or approximate length
            w = vol_cm3 * rho_ct
            od = wing_params.get('diag_spar_dia', 0.0)
            results.append(_row('Diag_Spars', 'diag_spar', '斜めスパー',
                                f"V={vol_cm3:.2f}cm³ (OD={od}mm)",
                                w, 'メッシュ体積 × ρ (傾斜のため)'))

        # Stringers: 解析的計算
        if 'stringer' in category_data:
            d = category_data['stringer']
            span_m = d['bbox_span_m']
            s_data = wing_params.get('stringers_data', [])
            total_area_mm2 = sum(s.get('width', 0) * s.get('depth', 0) for s in s_data)
            area_cm2 = total_area_mm2 / 100.0
            w = (span_m * 100.0) * area_cm2 * rho_str
            results.append(_row('Stringers', 'stringer', 'ストリンガー',
                                f"L≈{span_m*1000:.1f}mm, Area={total_area_mm2:.1f}mm²",
                                w, '解析的計算(断面×長) × ρ'))

        # X-Brace Wires: バウンディングスパン合計×線密度
        if 'xbrace' in category_data:
            d = category_data['xbrace']
            # swept mesh の長さはbbox_span_mで近似
            total_len_m = d['bbox_span_m']
            w = total_len_m * lam_xb
            results.append(_row('XBraceWires', 'xbrace', 'X-ブレースワイヤー',
                                f"L≈{total_len_m*1000:.1f}mm",
                                w, 'L × 線密度'))

        # Carbon Ribs: 面積（片面）×（カーボン面密度 + 接着剤面密度）
        if 'carbon_ribs' in category_data:
            d = category_data['carbon_ribs']
            one_side_m2 = d['area_m2'] / 2.0  # 薄板なので両面÷2
            w = one_side_m2 * (sigma_cr + sigma_cr_adh)
            results.append(_row('CarbonRibs', 'carbon_ribs', 'カーボンリブ',
                                f"A(片面)={one_side_m2*1e4:.1f}cm²",
                                w, 'A × (σ_carbon + σ_adhesive)'))

        # TE Caps + Rib Cap: 面積（片面）×（カーボン面密度 + 接着剤面密度）
        cap_vol = 0.0
        cap_area = 0.0
        if 'te_cap' in category_data:
            cap_area += category_data['te_cap']['area_m2']
        if 'rib_cap' in category_data:
            cap_area += category_data['rib_cap']['area_m2']
        if cap_area > 0.0:
            one_side_m2 = cap_area / 2.0
            w = one_side_m2 * (sigma_cap + sigma_cap_adh)
            results.append(_row('Caps', 'cap', 'カーボンキャップ (TE + Rib)',
                                f"A(片面)={one_side_m2*1e4:.1f}cm²",
                                w, 'A × (σ_carbon + σ_adhesive)'))

        # OPP Film: 表面積×面密度
        if 'film' in category_data:
            d = category_data['film']
            # フィルムは外面のみ: area/2 (上下面のうち外側)
            outer_area = d['area_m2'] / 2.0
            w = outer_area * sigma_film
            results.append(_row('Film_Skin', 'film', 'OPPフィルム',
                                f"A(外面)={outer_area*1e4:.1f}cm²",
                                w, 'A × σ_film'))

        # --- 解析的計算（3Dなし）---
        # 両面テープ: (Σリブ周長 + 後縁長×3) × 線密度
        lam_tape = mat_props.get('tape_linear_density', 5.0)
        if extra_analytics:
            perims = extra_analytics.get('rib_perimeters_mm', [])
            te_span = extra_analytics.get('te_span_mm', 0.0)
            total_perim_m = sum(perims) / 1000.0
            te_contrib_m = te_span * 3.0 / 1000.0
            tape_len_m = total_perim_m + te_contrib_m
            tape_w = tape_len_m * lam_tape
            results.append(_row('Tape', 'tape', '両面テープ',
                                f"L={tape_len_m*1000:.1f}mm (リブ周長合計{total_perim_m*1000:.0f}mm + TE×3={te_contrib_m*1000:.0f}mm)",
                                tape_w, 'L × 線密度'))
        else:
            # 解析値がない場合はプレースホルダ
            results.append(_row('Tape', 'tape', '両面テープ',
                                '要パラメータ計算', 0.0, '手入力モード'))

        return results


def _row(name, category, display_name, quantity_str, weight_g, note):
    return {
        'name': name,
        'category': category,
        'display_name': display_name,
        'quantity_str': quantity_str,
        'weight_g': weight_g,
        'note': note,
    }
