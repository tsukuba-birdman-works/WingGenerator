# ==========================================
# 3Dモデル用 マテリアル（色）定義
# (R, G, B, Alpha) の順で 0〜255 の値で指定します
# ==========================================

AVAILABLE_MATERIALS = {
    'Styrofoam (Blue)': [135, 206, 235, 255],       # スタイロ（水色）
    'Carbon (Gloss)': [30, 30, 30, 255],            # カーボン（グロス黒）
    'Carbon (Semi-Gloss)': [30, 30, 30, 255],       # カーボン（セミグロス黒）
    'Wood (Brown)': [205, 170, 125, 255],           # 木（茶色）
    'Ethylene Sheet (White)': [240, 240, 240, 255], # エスレンシート（白）
    'Kevlar (Yellow)': [240, 230, 140, 255],        # ケブラー（黄色）
    'OPP Film (Clear)': [250, 250, 255, 80],        # フィルム（半透明）
    'Default (Gray)': [200, 200, 200, 255]          # デフォルト（グレー）
}

# (metallicFactor, roughnessFactor)
# PBR properties for realistic rendering
MATERIAL_PBR_PROPERTIES = {
    'Styrofoam (Blue)': (0.0, 0.9),
    'Carbon (Gloss)': (0.3, 0.1),        # Glossy carbon
    'Carbon (Semi-Gloss)': (0.2, 0.4),   # Semi-gloss carbon
    'Wood (Brown)': (0.0, 0.8),          # Wood is very rough, no metallic
    'Ethylene Sheet (White)': (0.0, 0.6),# Semi-rough plastic
    'Kevlar (Yellow)': (0.1, 0.7),       # Fabric-like
    'OPP Film (Clear)': (0.0, 0.0),      # Very smooth, glossy film
    'Default (Gray)': (0.1, 0.5)
}
