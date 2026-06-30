import re

with open("ui/base_mode.py", "r") as f:
    code = f.read()

code = code.replace("self.pm.obj.tabs_frames['CNC'] = f_tab_outer", "self.pm.obj.tabs_frames['CNC'] = parent_frame")

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Export G-Code button moved inside the scrollable frame!")

with open("ui/param_spec.py", "r") as f:
    pcode = f.read()

# Add washout_exp to Other tab
new_param = """
    {'id': 'washout_exp', 'type': 'float', 'default': '1.0', 'tab': 'Other', 'group': 'Other', 'label': 'Washout Exponent', 'widget': 'entry'},
"""
pcode = pcode.replace("]\n\nSINGLE_PARAMS", new_param + "]\n\nSINGLE_PARAMS")
pcode = pcode.replace("]\n", new_param + "]\n", 1) # Add to SINGLE_PARAMS as well

with open("ui/param_spec.py", "w") as f:
    f.write(pcode)

