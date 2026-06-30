import re

with open("ui/base_mode.py", "r") as f:
    code = f.read()

# Add new variables
var_additions = """        self.truss_tab_width = tk.StringVar(value="4.0")
        self.tab_thickness = tk.StringVar(value="3.0")
        self.outer_tab_width = tk.StringVar(value="6.0")
        self.outer_tab_interval = tk.StringVar(value="100.0")
        self.tab_angle_deg = tk.StringVar(value="45.0")"""
        
code = re.sub(r"        self\.truss_tab_width = tk\.StringVar\(value=\"4\.0\"\)\n        self\.tab_thickness = tk\.StringVar\(value=\"3\.0\"\)", var_additions, code)

# Update create_cam_ui
ui_replacement = """        lf_truss = tk.LabelFrame(left_panel, text="Holding Tabs")
        lf_truss.pack(fill=tk.X, pady=5)
        
        tk.Label(lf_truss, text="Inner Tab Base Width (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.truss_tab_width, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(lf_truss, text="Outer Tab Base Width (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.outer_tab_width, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(lf_truss, text="Outer Tab Interval (mm):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.outer_tab_interval, width=8).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        tk.Label(lf_truss, text="Tab Thickness Z (mm):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_thickness, width=8).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(lf_truss, text="Tab Z Angle (deg):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_angle_deg, width=8).grid(row=4, column=1, sticky="w", padx=5, pady=2)"""

code = re.sub(r"        lf_truss = tk\.LabelFrame\(left_panel, text=\"Truss Tabs\"\)\n        lf_truss\.pack\(fill=tk\.X, pady=5\)\n        tk\.Label\(lf_truss, text=\"Tab Width \(mm\):\"\)\.grid\(row=0, column=0, sticky=\"e\", padx=5, pady=5\)\n        tk\.Entry\(lf_truss, textvariable=self\.truss_tab_width, width=8\)\.grid\(row=0, column=1, sticky=\"w\", padx=5, pady=5\)\n        tk\.Label\(lf_truss, text=\"Tab Thickness Z \(mm\):\"\)\.grid\(row=1, column=0, sticky=\"e\", padx=5, pady=5\)\n        tk\.Entry\(lf_truss, textvariable=self\.tab_thickness, width=8\)\.grid\(row=1, column=1, sticky=\"w\", padx=5, pady=5\)", ui_replacement, code)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("step1_ui.py applied")
