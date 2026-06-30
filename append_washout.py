import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

new_param = "    {'id': 'washout_exp', 'type': 'float', 'default': 1.0, 'tab': 'Other', 'group': 'Other', 'label': 'Washout Exponent', 'widget': 'entry'},\n"

# Append before the end of BATCH_PARAMS list
code = re.sub(r"\]\n\nSINGLE_PARAMS", new_param + "]\n\nSINGLE_PARAMS", code)

# Append before the end of SINGLE_PARAMS list
code = re.sub(r"\]\n$", new_param + "]\n", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Appended!")
