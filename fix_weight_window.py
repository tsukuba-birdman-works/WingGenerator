with open('ui/weight_window.py', 'r', encoding='utf-8') as f:
    text = f.read()

replaces = [
    ('self.title("Weight Calculator")', 'self.title("重量計算 (Weight Calculator)")'),
    ('text="Material Properties & Densities"', 'text="材料物性値・密度"'),
    ('text="Calculate Weight"', 'text="重量を計算する"'),
    ('text="Weight Report"', 'text="重量レポート"'),
    ('text="Category"', 'text="カテゴリ"'),
    ('text="Part Name"', 'text="部品名"'),
    ('text="Quantity / Formula"', 'text="数量 / 計算式"'),
    ('text="Weight (g)"', 'text="重量 (g)"'),
    ('text="Note"', 'text="備考"'),
    ('text="Total Weight: 0.00 g"', 'text="総重量: 0.00 g"'),
    ('text="Generating geometry... Please wait."', 'text="3D形状を生成中... お待ちください"'),
    ('text="Done."', 'text="完了"'),
    ('text="Error occurred."', 'text="エラーが発生しました"'),
    ('text=f"Total Weight: {total_w:.2f} g"', 'text=f"総重量: {total_w:.2f} g"'),
    ('messagebox.showerror("Error"', 'messagebox.showerror("エラー"'),
]

for old, new in replaces:
    text = text.replace(old, new)

with open('ui/weight_window.py', 'w', encoding='utf-8') as f:
    f.write(text)
