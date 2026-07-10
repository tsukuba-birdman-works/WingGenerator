import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

target1 = """        if 'Xブレース' in self.pm.obj.groups_frames:"""
replacement1 = """        if '翼全体' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['翼全体'], text="Generate Positions", command=self.calculate_y_positions).pack(fill=tk.X, padx=10, pady=5)

        if 'Xブレース' in self.pm.obj.groups_frames:"""

if target1 in text:
    text = text.replace(target1, replacement1)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
    print("Re-added Generate Positions button")

