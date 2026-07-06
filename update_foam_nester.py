import re

with open('foam_nester.py', 'r') as f:
    code = f.read()

# 1. Update setup_ui left frame
# Find Transformations section
ui_replacement = """        ttk.Label(left_frame, text="Material Height (Y):").pack()
        self.mat_height = tk.DoubleVar(value=100.0)
        tk.Spinbox(left_frame, from_=10.0, to=500.0, increment=5.0, textvariable=self.mat_height, command=self.update_plot).pack(fill=tk.X, pady=2)
        self.mat_height.trace_add('write', lambda *a: self.update_plot())
        
        self.lbl_warning = tk.Label(left_frame, text="", fg="red", font=("Helvetica", 10, "bold"))
        self.lbl_warning.pack(fill=tk.X, pady=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text="Transformations").pack()
        
        ttk.Label(left_frame, text="Rotation (deg):").pack()
        self.angle_var = tk.DoubleVar(value=0.0)
        self.scale_rot = tk.Scale(left_frame, variable=self.angle_var, from_=-180, to=180, orient="horizontal", command=self.on_angle_change)
        self.scale_rot.pack(fill=tk.X, pady=2)

        ttk.Button(left_frame, text="Mirror L/R (Swap & Flip)", command=lambda: self.transform('swap_flip')).pack(fill=tk.X, pady=5)"""

pattern_ui = r'ttk\.Label\(left_frame, text="Transformations"\)\.pack\(\).*?ttk\.Button\(left_frame, text="Swap XY / AZ"[^\n]*\.pack\([^\n]*\)'
code = re.sub(pattern_ui, ui_replacement, code, flags=re.DOTALL)


# 2. Update on_select to sync angle slider
sel_replacement = """    def on_select(self, event):
        idx = self.listbox.curselection()
        if idx:
            self.selected_idx = idx[0]
            self.angle_var.set(self.parts[self.selected_idx].angle_deg)
            self.update_plot()
            
    def on_angle_change(self, val):
        if self.selected_idx >= 0:
            self.parts[self.selected_idx].angle_deg = float(val)
            self.update_plot()"""
code = re.sub(r'    def on_select\(self, event\):.*?self\.update_plot\(\)', sel_replacement, code, flags=re.DOTALL)


# 3. Update transform to handle swap_flip
trans_replacement = """    def transform(self, action):
        if self.selected_idx < 0: return
        part = self.parts[self.selected_idx]
        if action == 'swap_flip':
            part.swap_xyaz = not part.swap_xyaz
            part.flip_x = not part.flip_x
        self.update_plot()"""
code = re.sub(r'    def transform\(self, action\):.*?self\.update_plot\(\)', trans_replacement, code, flags=re.DOTALL)

# 4. Update plot to draw material lines and check warning
# We need to insert code in update_plot before drawing canvas.
with open('foam_nester.py', 'w') as f:
    f.write(code)
print("Patch applied step 1")
