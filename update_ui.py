import sys

with open("ui/base_mode.py", "r") as f:
    code = f.read()

ui_rep = """        tk.Label(lf_truss, text="Tab Z Angle (deg):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_angle_deg, width=8).grid(row=4, column=1, sticky="w", padx=5, pady=2)

        tk.Label(lf_truss, text="Exclusion (Stringer, mm):").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_exclusion_stringer, width=8).grid(row=5, column=1, sticky="w", padx=5, pady=2)

        tk.Label(lf_truss, text="Exclusion (LE/TE, mm):").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_exclusion_le_te, width=8).grid(row=6, column=1, sticky="w", padx=5, pady=2)"""

code = code.replace("""        tk.Label(lf_truss, text="Tab Z Angle (deg):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_angle_deg, width=8).grid(row=4, column=1, sticky="w", padx=5, pady=2)""", ui_rep)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Updated base_mode.py UI")
