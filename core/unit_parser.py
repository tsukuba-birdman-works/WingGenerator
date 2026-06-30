"""
単位付き数値パーサー
「1600 kg/m^3」や「50 g/m²」のような入力を内部基本単位に自動変換する。

内部基本単位:
  体積密度  (volume_density)  → g/cm³
  面密度    (area_density)    → g/m²
  線密度    (linear_density)  → g/m
  重量      (weight_g)        → g  （変換なし、数値のみ）
"""

import re
from typing import Tuple

# ==============================================================
# 変換テーブル: 各単位 → 基本単位 の係数
# ==============================================================

# 体積密度 → g/cm³
_VOL = {
    # g/cm³ (基本)
    'g/cm3':   1.0,
    'g/cc':    1.0,
    'g/ml':    1.0,
    # kg/m³
    'kg/m3':   1e-3,
    # kg/L, kg/dm³ (= 1 g/cm³)
    'kg/l':    1.0,
    'kg/dm3':  1.0,
    # mg/cm³
    'mg/cm3':  1e-3,
    # g/mm³
    'g/mm3':   1e3,
    # mg/mm³
    'mg/mm3':  1.0,
    # t/m³ (= kg/dm³ = 1 g/cm³)
    't/m3':    1.0,
    # lb/in³
    'lb/in3':  27.6799,
    # lb/ft³
    'lb/ft3':  0.0160185,
}

# 面密度 → g/m²
_AREA = {
    # g/m² (基本)
    'g/m2':    1.0,
    'gsm':     1.0,       # grams per square metre
    # kg/m²
    'kg/m2':   1e3,
    # g/cm²
    'g/cm2':   1e4,
    # g/dm²
    'g/dm2':   1e2,
    # mg/m²
    'mg/m2':   1e-3,
    # oz/yd²
    'oz/yd2':  33.906,
    # g/ft²
    'g/ft2':   10.7639,
}

# 線密度 → g/m
_LIN = {
    # g/m (基本)
    'g/m':     1.0,
    # kg/m
    'kg/m':    1e3,
    # g/cm
    'g/cm':    1e2,
    # g/mm
    'g/mm':    1e3,
    # mg/m
    'mg/m':    1e-3,
    # g/km
    'g/km':    1e-3,
    # tex (g/km)
    'tex':     1e-3,
    # dtex
    'dtex':    1e-4,
    # denier (g/9000m)
    'denier':  1.0 / 9.0 * 1e-3,
    'd':       1.0 / 9.0 * 1e-3,
}

# 重量 → g
_WEIGHT = {
    'g':    1.0,
    'kg':   1e3,
    'mg':   1e-3,
    'oz':   28.3495,
    'lb':   453.592,
}

_DIMENSION_TABLES = {
    'volume_density': (_VOL,    'g/cm³'),
    'area_density':   (_AREA,   'g/m²'),
    'linear_density': (_LIN,    'g/m'),
    'weight_g':       (_WEIGHT, 'g'),
}


# ==============================================================
# 正規化ヘルパー
# ==============================================================

def _normalize_unit(s: str) -> str:
    """
    単位文字列を正規化する。
    例: 'kg/m³' → 'kg/m3'
        'g/cm^2' → 'g/cm2'
        'G / M 2' → 'g/m2'
    """
    s = s.strip()
    # unicode 上付き文字
    s = s.replace('²', '2').replace('³', '3').replace('¹', '1')
    # ^ 指数表記: cm^3 → cm3, m^2 → m2
    s = re.sub(r'\^(\d+)', r'\1', s)
    # スペースを除去
    s = s.replace(' ', '')
    # * · を除去
    s = s.replace('*', '').replace('·', '')
    # 小文字化（ただし後で大文字バリアントも試す）
    return s.lower()


def _lookup(unit_str: str, table: dict) -> float | None:
    """テーブルを検索して変換係数を返す。見つからなければ None。"""
    normalized = _normalize_unit(unit_str)
    for key, factor in table.items():
        if _normalize_unit(key) == normalized:
            return factor
    return None


# ==============================================================
# メイン関数
# ==============================================================

def parse_value_with_unit(text: str, dimension: str) -> Tuple[float, str]:
    """
    単位付き（または単位なし）の数値文字列をパースし、
    基本単位に変換した値と変換メモを返す。

    Parameters
    ----------
    text : str
        例: '1600 kg/m3', '1.6 g/cm³', '50', '200 g/m^2'
    dimension : str
        'volume_density' | 'area_density' | 'linear_density' | 'weight_g'

    Returns
    -------
    (value_in_base_unit: float, note: str)
        note は変換が行われた場合にのみ設定される ('X unit → Y base_unit')
        単位なし・変換不要の場合は note = ''

    Raises
    ------
    ValueError
        単位が認識できない場合、または数値として解析できない場合
    """
    text = text.strip()
    if not text:
        return 0.0, ''

    # 純粋な数値（単位なし）
    try:
        return float(text), ''
    except ValueError:
        pass

    # 数値 + 単位 に分割（数値部: 整数/小数/科学表記）
    m = re.match(
        r'^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*(.+)$',
        text, re.IGNORECASE
    )
    if not m:
        raise ValueError(
            f"'{text}' を数値として解析できません。\n"
            f"例: '1.6', '1600 kg/m3', '50 g/m²'"
        )

    value = float(m.group(1))
    unit_str = m.group(2).strip()

    if dimension not in _DIMENSION_TABLES:
        raise ValueError(f"未知の次元: {dimension}")

    table, base_unit = _DIMENSION_TABLES[dimension]
    factor = _lookup(unit_str, table)

    if factor is None:
        available = ', '.join(table.keys())
        raise ValueError(
            f"単位 '{unit_str}' は {dimension} として認識できません。\n"
            f"使用可能な単位: {available}"
        )

    converted = value * factor
    if abs(factor - 1.0) > 1e-10:
        # 元の単位表現（ユーザー入力）を使いつつ基本単位に変換した旨を示す
        note = f"{value} {unit_str} → {converted:.6g} {base_unit}"
    else:
        note = ''

    return converted, note


def format_with_unit(value: float, dimension: str) -> str:
    """
    基本単位の数値を読みやすい文字列で返す（表示用）。
    例: 0.001 (g/cm³) → '0.001 g/cm³'
    """
    _, base_unit = _DIMENSION_TABLES.get(dimension, (None, ''))
    return f"{value:g} {base_unit}"
