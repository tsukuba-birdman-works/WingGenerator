with open('main.py', 'r') as f:
    text = f.read()

text = text.replace('root.title("Rib Generator - Mode Select")', 'root.title("Wing Generator - Mode Select")')
text = text.replace('tk.Label(root, text="Select Generation Mode", font=("Arial", 16, "bold")).pack(pady=(30, 20))', 'tk.Label(root, text="起動モード選択", font=("Arial", 16, "bold")).pack(pady=(30, 20))')
text = text.replace('text="Single Rib Mode\\n(単一リブ設計)"', 'text="単一リブ生成モード\\n(Single Rib Mode)"')
text = text.replace('text="Batch Wing Mode\\n(翼全体のリブ設計)"', 'text="一括翼生成モード\\n(Batch Mode)"')
text = text.replace('text="4-Axis Foam CAM\\n(フォームコア加工)"', 'text="フォームカッターCAM\\n(4-Axis Foam CAM)"')
text = text.replace('text="Wingtip Fin Gen\\n(翼端フィン設計)"', 'text="垂直尾翼生成モード\\n(Wingtip Fin Gen)"')

with open('main.py', 'w') as f:
    f.write(text)
