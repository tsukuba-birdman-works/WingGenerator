import re

for filename in ["ui/batch_mode.py", "ui/single_mode.py"]:
    with open(filename, "r") as f:
        code = f.read()
    
    # Replace the old dict comprehension with one that searches self.pm.vars
    old_dict_comp = "**{k: getattr(self, k).get() for k in ['safe_margin_var', 'te_cap_uf_act', 'te_cap_lf_act', 'te_cap_ur_act', 'te_cap_lr_act', 'rc1_act', 'rc2_act', 'diag1_active', 'diag2_active'] if hasattr(self, k)},"
    
    new_dict_comp = "**{k: self.pm.vars[k].get() for k in ['safe_margin_var', 'te_cap_uf_act', 'te_cap_lf_act', 'te_cap_ur_act', 'te_cap_lr_act', 'rc1_act', 'rc2_act', 'diag1_active', 'diag2_active'] if k in self.pm.vars},"
    
    code = code.replace(old_dict_comp, new_dict_comp)
    code = code.replace("textvariable=self.pm.vars['local_angle_var']", "textvariable=self.local_truss_angle")
    
    with open(filename, "w") as f:
        f.write(code)

