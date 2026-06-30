import re

with open("ui/base_mode.py", "r") as f:
    code = f.read()

replacement = """    def get_cam_vars(self):
        return {
            'tabs_active': self.tabs_active,
            'truss_tab_width': self.truss_tab_width,
            'outer_tab_width': getattr(self, 'outer_tab_width', self.truss_tab_width),
            'outer_tab_interval': getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")),
            'tab_angle_deg': getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")),
            'main_spar_support_w': self.main_spar_support_w,"""

code = re.sub(r"    def get_cam_vars\(self\):\n        return \{\n            'tabs_active': self\.tabs_active,\n            'truss_tab_width': self\.truss_tab_width,\n            'main_spar_support_w': self\.main_spar_support_w,", replacement, code)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("step2_vars.py applied")
