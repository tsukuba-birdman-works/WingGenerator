with open('ui/ui_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add translation dictionaries
translations = """import tkinter as tk
from tkinter import ttk

TAB_TRANSLATIONS = {
    'Wing': '翼設定',
    'Spar': '桁設定',
    'PlankTE': 'プランク・後縁',
    'Rib': 'リブ・肉抜き',
    'Brace&Connector': 'ブレース・コネクタ',
    'Foam': 'フォーム・治具',
    'DXF': 'DXF出力',
    'CNC': 'CNC設定',
    'Export3D': '3Dエクスポート'
}

GROUP_TRANSLATIONS = {
    'Layout': 'レイアウト',
    'Airfoil (Root)': '翼型 (根元)',
    'LE Interpolation': '前縁補間',
    'Airfoil (Tip)': '翼型 (翼端)',
    'Front Spar': '前桁 (Front Spar)',
    'Main Spar': '主桁 (Main Spar)',
    'Rear Spar': '後桁 (Rear Spar)',
    'Root Bolt 1': '根元ボルト 1',
    'Root Bolt 2': '根元ボルト 2',
    'Tip Bolt 1': '翼端ボルト 1',
    'Tip Bolt 2': '翼端ボルト 2',
    'Bolt Spacers & Margins': 'ボルトスペーサ＆マージン',
    'Plank Skin': 'プランク外板',
    'TE Cut & Thick': '後縁カット＆厚み',
    'Stringers': 'ストリンガー',
    'General': '基本設定',
    'Truss & Margins': 'トラス＆マージン',
    'Root Carbon Rib': '根元カーボンリブ',
    'Tip Carbon Rib': '翼端カーボンリブ',
    'Cross Bracing': 'Xブレース',
    'Connectors': 'コネクタ',
    'Diag Connector 1': '斜めコネクタ 1',
    'Diag Connector 2': '斜めコネクタ 2',
    'Joint Sleeve 1': 'ジョイントスリーブ 1',
    'Joint Sleeve 2': 'ジョイントスリーブ 2',
    'Rib Cap 1': 'リブキャップ 1',
    'Rib Cap 2': 'リブキャップ 2',
    'Jig Settings': '治具設定',
    'Layers': 'レイヤー設定',
    'Options': '出力オプション',
    'Foam Cutter': 'フォームカッター',
    'Materials': 'マテリアル(色)',
    'Parts Output': 'パーツ出力対象'
}
"""

if "TAB_TRANSLATIONS =" not in text:
    text = text.replace("import tkinter as tk\nfrom tkinter import ttk", translations)

    # Apply translations when creating tabs
    text = text.replace("notebook.add(f_tab_outer, text=tab_name)", "notebook.add(f_tab_outer, text=TAB_TRANSLATIONS.get(tab_name, tab_name))")
    
    # Apply translations when creating groups (LabelFrame)
    text = text.replace("lf = ttk.LabelFrame(col_frame, text=g)", "lf = ttk.LabelFrame(col_frame, text=GROUP_TRANSLATIONS.get(g, g))")

with open('ui/ui_builder.py', 'w', encoding='utf-8') as f:
    f.write(text)
