import re

# 1. Update single_mode.py and batch_mode.py window size
for filename in ["ui/single_mode.py", "ui/batch_mode.py"]:
    with open(filename, "r") as f:
        code = f.read()
    
    # insert self.master.geometry("1400x900") after self.master.title(...)
    code = re.sub(r'(self\.master\.title\([^\)]+\))', r'\1\n        self.master.geometry("1400x900")', code)
    
    with open(filename, "w") as f:
        f.write(code)

# 2. Update base_mode.py to correctly save ALL variables
with open("ui/base_mode.py", "r") as f:
    code = f.read()

get_all_vars_patch = """
    def get_all_vars(self):
        # Base param_spec vars
        vars_dict = self.pm.get_all_vars() if hasattr(self, 'pm') else {}
        # Merge manual CAM vars
        if hasattr(self, 'get_cam_vars'):
            vars_dict.update(self.get_cam_vars())
        # Merge manual Stringer vars
        if hasattr(self, 'str_vars'):
            for name, d in self.str_vars.items():
                vars_dict[f"str_{name}_active"] = d['active']
                vars_dict[f"str_{name}_pos"] = d['pos']
                vars_dict[f"str_{name}_w"] = d['w']
                vars_dict[f"str_{name}_d"] = d['d']
                vars_dict[f"str_{name}_use_dxf"] = d['use_dxf']
                vars_dict[f"str_{name}_dxf"] = d['dxf']
        return vars_dict
"""

# Insert get_all_vars_patch before `def get_stringers_data`
code = code.replace("    def get_stringers_data(self):", get_all_vars_patch.strip('\n') + "\n\n    def get_stringers_data(self):")

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Window size and get_all_vars patched!")
