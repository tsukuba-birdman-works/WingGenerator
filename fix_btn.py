import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

old_btn = """        # Add Generate Positions button into Wing Tab
        if '翼全体' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['翼全体'], text="Generate Positions", command=self.calculate_y_positions).pack(fill=tk.X, padx=10, pady=5)"""

text = text.replace(old_btn, "")

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)
