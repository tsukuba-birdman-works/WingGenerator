import sys

with open("ui/batch_mode.py", "r") as f:
    code = f.read()

batch_rep = """            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_thickness', tk.StringVar(value="3.0")), 3.0),
            'outer_tab_width': getattr(self, 'safe_float')(getattr(self, 'outer_tab_width', tk.StringVar(value="6.0")), 6.0),
            'outer_tab_interval': getattr(self, 'safe_float')(getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")), 100.0),
            'tab_angle_deg': getattr(self, 'safe_float')(getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")), 45.0),
            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
        }"""

code = code.replace("""            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_thickness', tk.StringVar(value="3.0")), 3.0),
            'outer_tab_width': getattr(self, 'safe_float')(getattr(self, 'outer_tab_width', tk.StringVar(value="6.0")), 6.0),
            'outer_tab_interval': getattr(self, 'safe_float')(getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")), 100.0),
            'tab_angle_deg': getattr(self, 'safe_float')(getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")), 45.0),
        }""", batch_rep)

with open("ui/batch_mode.py", "w") as f:
    f.write(code)

print("Updated batch_mode.py params")
