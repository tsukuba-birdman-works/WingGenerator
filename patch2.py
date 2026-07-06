import re

with open('ui/foam_mode.py', 'r') as f:
    content = f.read()

ui_addition = """
        self.reverse_path = tk.BooleanVar(value=False)
        tk.Checkbutton(pf, text="Reverse Direction", variable=self.reverse_path, command=self.update_preview).grid(row=7, column=1, sticky="w", pady=2)
        
        tk.Label(pf, text="Rotation (deg):").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        rf = tk.Frame(pf)
        rf.grid(row=8, column=1, sticky="w")
        self.rotation_angle = tk.DoubleVar(value=0.0)
        tk.Entry(rf, textvariable=self.rotation_angle, width=5).pack(side="left")
        tk.Button(rf, text="Auto Optimize", command=self.optimize_rotation).pack(side="left", padx=5)
        self.rotation_angle.trace_add("write", lambda *args: self.update_preview())
        
        self.smooth_curves = tk.BooleanVar(value=False)
        tk.Checkbutton(pf, text="Smooth Curves", variable=self.smooth_curves, command=self.update_preview).grid(row=9, column=1, sticky="w", pady=2)

        tk.Label(pf, text="Axes (L_h, L_v, R_h, R_v):").grid(row=10, column=0, sticky="e", padx=5, pady=5)
"""
content = content.replace('        tk.Label(pf, text="Axes (L_h, L_v, R_h, R_v):").grid(row=7, column=0, sticky="e", padx=5, pady=5)', ui_addition)

content = content.replace('af.grid(row=7', 'af.grid(row=10')
content = content.replace('grid(row=8', 'grid(row=11')
content = content.replace('hf.grid(row=8', 'hf.grid(row=11')
content = content.replace('grid(row=9', 'grid(row=12')
content = content.replace('wt_frame.grid(row=9', 'wt_frame.grid(row=12')

# Pass kwargs to compute_trajectory
old_call = "auto_center=False"
new_call = "auto_center=False, reverse_path=self.reverse_path.get(), smooth_curves=self.smooth_curves.get(), rotation_angle=self.rotation_angle.get()"
content = content.replace(old_call, new_call)

with open('ui/foam_mode.py', 'w') as f:
    f.write(content)
