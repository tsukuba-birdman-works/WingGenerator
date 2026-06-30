import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# Delete local_angle_var from BATCH_PARAMS and SINGLE_PARAMS
code = re.sub(r"\s*\{'id': 'local_angle_var'[^}]+\},", "", code)

# Move safe_margin_var to Rib tab
code = re.sub(r"'tab': 'Other', 'group': 'Other', 'label': 'safe_margin_var'", r"'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Safe Margin'", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

with open("ui/batch_mode.py", "r") as f:
    code = f.read()

# Change the entry to use self.local_truss_angle
code = code.replace("textvariable=self.pm.vars['local_angle_var']", "textvariable=self.local_truss_angle")

# Fix getattr(self, 'safe_margin_var') to read from self.pm.vars
code = code.replace("getattr(self, k).get() for k in ['safe_margin_var'", "self.pm.vars[k].get() for k in ['safe_margin_var'")
# Wait, let's just make a safe wrapper
# If 'safe_margin_var' is in the loop, we can change the list comprehension.
# Let's replace the dictionary comprehension for kwargs.
# Actually, the dictionary comprehension is:
# **{k: getattr(self, k).get() for k in ['safe_margin_var', 'te_cap_uf_act', ...] if hasattr(self, k)}
# Wait, none of those variables are in `self` anymore! They are in `self.pm.vars`!
# Oh my god!

