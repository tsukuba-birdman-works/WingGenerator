import re
import os

filepath = 'ui/single_mode.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add missing Variables to __init__
var_init = """
        # Restored vars for single mode
        self.margin_outer_edge = getattr(self, 'margin_outer_edge', tk.StringVar(value="2.0"))
        self.plank_part_start = getattr(self, 'plank_part_start', tk.StringVar(value="0.0"))
        self.plank_part_end = getattr(self, 'plank_part_end', tk.StringVar(value="100.0"))
        self.root_bolt1_dx = getattr(self, 'root_bolt1_dx', tk.StringVar(value="0.0"))
        self.root_bolt1_dy = getattr(self, 'root_bolt1_dy', tk.StringVar(value="0.0"))
        self.root_bolt1_dia = getattr(self, 'root_bolt1_dia', tk.StringVar(value="0.0"))
        self.root_bolt2_dx = getattr(self, 'root_bolt2_dx', tk.StringVar(value="0.0"))
        self.root_bolt2_dy = getattr(self, 'root_bolt2_dy', tk.StringVar(value="0.0"))
        self.root_bolt2_dia = getattr(self, 'root_bolt2_dia', tk.StringVar(value="0.0"))
        self.local_truss_angle = getattr(self, 'local_truss_angle', tk.StringVar(value="0.0"))
        self.export_carbon_ribs = getattr(self, 'export_carbon_ribs', tk.BooleanVar(value=True))
"""
if "self.margin_outer_edge =" not in content:
    idx = content.find("self.create_stringers_tab(notebook)")
    content = content[:idx] + var_init + content[idx:]

# 2. Add to UI
ui_inj = """
        # Restored UI fields
        tk.Label(tab_main, text="Plank Part S/E:").grid(row=13, column=0, sticky="e", padx=5, pady=5)
        f_p = tk.Frame(tab_main); f_p.grid(row=13, column=1, sticky="w")
        tk.Entry(f_p, textvariable=self.plank_part_start, width=5).pack(side=tk.LEFT)
        tk.Entry(f_p, textvariable=self.plank_part_end, width=5).pack(side=tk.LEFT)

        tk.Label(tab_main, text="Root Bolt 1 (dX/dY/Dia):").grid(row=14, column=0, sticky="e", padx=5, pady=5)
        f_b1 = tk.Frame(tab_main); f_b1.grid(row=14, column=1, sticky="w")
        tk.Entry(f_b1, textvariable=self.root_bolt1_dx, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b1, textvariable=self.root_bolt1_dy, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b1, textvariable=self.root_bolt1_dia, width=4).pack(side=tk.LEFT)

        tk.Label(tab_main, text="Root Bolt 2 (dX/dY/Dia):").grid(row=15, column=0, sticky="e", padx=5, pady=5)
        f_b2 = tk.Frame(tab_main); f_b2.grid(row=15, column=1, sticky="w")
        tk.Entry(f_b2, textvariable=self.root_bolt2_dx, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b2, textvariable=self.root_bolt2_dy, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b2, textvariable=self.root_bolt2_dia, width=4).pack(side=tk.LEFT)

        tk.Label(tab_truss, text="Margin Outer (Norm/Edge):").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_truss, textvariable=self.margin_outer_edge, width=6).grid(row=7, column=1, sticky="w", padx=5)
        
        tk.Label(tab_truss, text="Local Truss Angle:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_truss, textvariable=self.local_truss_angle, width=6).grid(row=8, column=1, sticky="w", padx=5)
"""
if "Root Bolt 1" not in content:
    idx = content.find("self.create_stringers_tab(notebook)")
    content = content[:idx] + ui_inj + content[idx:]

# 3. Fix the broken safe_float call
broken = "spar_tab_width=self.safe_float(self.main_spar_support_w, self.main_spar_support_h, self.main_spar_support_thick, 6.0)"
fixed = "spar_tab_width=self.safe_float(self.main_spar_support_w, 4.0)"
content = content.replace(broken, fixed)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Single mode patched")
