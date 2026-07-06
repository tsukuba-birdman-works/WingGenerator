import re

with open('ui/foam_mode.py', 'r') as f: code = f.read()

# Add the button
btn_code = """        tk.Button(rf, text="Auto Optimize", command=self.optimize_rotation).pack(side="left", padx=5)
        tk.Button(rf, text="Min Thickness (Y,Z)", command=self.optimize_rotation_yz).pack(side="left", padx=5)"""
code = code.replace('        tk.Button(rf, text="Auto Optimize", command=self.optimize_rotation).pack(side="left", padx=5)', btn_code)

# Add the handler method
handler_code = """    def optimize_rotation_yz(self):
        root_path = self.root_profile_path.get()
        tip_path = self.tip_profile_path.get()
        f1, f2 = (tip_path, root_path) if self.wing_type.get() == "Right" else (root_path, tip_path)
        try:
            ox = float(self.offset_x.get())
            oy = float(self.offset_y.get())
            opt_angle = self.engine.find_optimal_rotation_yz(f1, f2, ox, oy)
            self.rotation_angle.set(round(opt_angle, 1))
            self.update_preview()
        except Exception as e:
            print(f"Optimization YZ error: {e}")

    def optimize_rotation"""
code = code.replace('    def optimize_rotation', handler_code, 1)

with open('ui/foam_mode.py', 'w') as f: f.write(code)
