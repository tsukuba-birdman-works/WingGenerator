import re

with open('ui/foam_mode.py', 'r') as f:
    content = f.read()

# Add rotation_angle var and UI
ui_code = """
        tk.Label(pf, text="Rotation (deg):").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        rf = tk.Frame(pf)
        rf.grid(row=8, column=1, sticky="w")
        self.rotation_angle = tk.DoubleVar(value=0.0)
        tk.Entry(rf, textvariable=self.rotation_angle, width=5).pack(side="left")
        tk.Button(rf, text="Auto Optimize", command=self.optimize_rotation).pack(side="left", padx=5)
        self.rotation_angle.trace_add("write", lambda *args: self.update_preview())
"""
content = content.replace("        self.smooth_curves = tk.BooleanVar(value=False)", ui_code + "\n        self.smooth_curves = tk.BooleanVar(value=False)")

# Pass rotation_angle to compute_trajectory
content = content.replace(
    "auto_center=False, reverse_path=self.reverse_path.get(), smooth_curves=self.smooth_curves.get()",
    "auto_center=False, reverse_path=self.reverse_path.get(), smooth_curves=self.smooth_curves.get(), rotation_angle=self.rotation_angle.get()"
)

# Add optimize_rotation method
method_code = """
    def optimize_rotation(self):
        root_path = self.root_profile_path.get()
        tip_path = self.tip_profile_path.get()
        f1, f2 = (tip_path, root_path) if self.wing_type.get() == "Right" else (root_path, tip_path)
        try:
            opt_angle = self.engine.find_optimal_rotation(f1, f2)
            self.rotation_angle.set(round(opt_angle, 1))
        except Exception as e:
            print(f"Optimization error: {e}")
"""
content = content.replace("    def browse_file(self, var):", method_code + "\n    def browse_file(self, var):")

with open('ui/foam_mode.py', 'w') as f:
    f.write(content)
print("foam_mode patched")
