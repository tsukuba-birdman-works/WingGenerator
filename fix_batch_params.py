import re

with open("ui/batch_mode.py", "r") as f:
    code = f.read()

replacement = """            'main_spar_support_h': ms_tab_d,
            'main_spar_support_thick': 3.0,
            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_thickness', tk.StringVar(value="3.0")), 3.0),
            'outer_tab_width': getattr(self, 'safe_float')(getattr(self, 'outer_tab_width', tk.StringVar(value="6.0")), 6.0),
            'outer_tab_interval': getattr(self, 'safe_float')(getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")), 100.0),
            'tab_angle_deg': getattr(self, 'safe_float')(getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")), 45.0),
        }"""

code = code.replace("""            'main_spar_support_h': ms_tab_d,
            'main_spar_support_thick': 3.0,
            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_thickness', tk.StringVar(value="3.0")), 3.0),
        }""", replacement)

with open("ui/batch_mode.py", "w") as f:
    f.write(code)

print("Batch mode parameters fixed!")
