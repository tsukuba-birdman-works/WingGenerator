import sys

with open("ui/base_mode.py", "r") as f:
    code = f.read()

# 1. Update init_cam_variables
init_rep = """        self.tab_angle_deg = tk.StringVar(value="45.0")
        self.tab_exclusion_stringer = tk.StringVar(value="10.0")
        self.tab_exclusion_le_te = tk.StringVar(value="30.0")"""
code = code.replace('        self.tab_angle_deg = tk.StringVar(value="45.0")', init_rep)

# 2. Update get_cam_vars
vars_rep = """            'tab_angle_deg': getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")),
            'tab_exclusion_stringer': getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")),
            'tab_exclusion_le_te': getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")),"""
code = code.replace("            'tab_angle_deg': getattr(self, 'tab_angle_deg', tk.StringVar(value=\"45.0\")),", vars_rep)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Updated base_mode.py vars")
