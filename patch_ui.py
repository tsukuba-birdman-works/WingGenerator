import re

with open('ui/batch_mode.py', 'r') as f:
    content = f.read()

# 1. Add te_cap_thick to the float list
pattern_floats = r"\[\'joint_length\', \'wing_span\', (.*?), \'cr_thick\'(.*?)\]"
# Let's just find "cr_thick', " and insert "te_cap_thick', "
content = content.replace("'cr_thick', 'rc1_start'", "'cr_thick', 'te_cap_thick', 'rc1_start'")

# 2. Add material comboboxes to the UI
materials_code = """
        ttk.Separator(tab_export3d, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_export3d, text="Materials", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        
        mat_opts = ['Styrofoam (Blue)', 'Carbon (Black)', 'Wood (Brown)', 'Kevlar (Yellow)', 'OPP Film (Clear)', 'Metal (Silver)']
        
        mat_vars = [
            ("Ribs", self.mat_ribs), ("Carbon Ribs", self.mat_carbon_ribs),
            ("Main Spar", self.mat_main_spar), ("Front/Rear Spars", self.mat_front_spar),
            ("Plank", self.mat_plank), ("TE/Rib Caps", self.mat_te_caps),
            ("X-Brace", self.mat_xbrace_wires), ("Connectors", self.mat_connectors),
            ("Stringers", self.mat_stringers), ("Film", self.mat_film)
        ]
        
        for i, (name, var) in enumerate(mat_vars):
            ttk.Label(tab_export3d, text=name+":").grid(row=row_idx + i//2, column=(i%2)*2, sticky=tk.E, padx=5, pady=2)
            ttk.Combobox(tab_export3d, textvariable=var, values=mat_opts, width=15).grid(row=row_idx + i//2, column=(i%2)*2 + 1, sticky=tk.W, padx=5, pady=2)
            
        row_idx += (len(mat_vars) // 2) + 1
"""

target = "        ttk.Separator(tab_export3d, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1\n        ttk.Button(tab_export3d, text=\"Export 3D Model (.glb)\", command=self.export_obj).grid(row=row_idx, column=0, columnspan=2, pady=10)"

content = content.replace(target, materials_code + "\n" + target)

with open('ui/batch_mode.py', 'w') as f:
    f.write(content)

print("Patched!")
