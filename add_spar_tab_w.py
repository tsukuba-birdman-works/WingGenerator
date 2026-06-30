import re

with open("ui/param_spec.py", "r") as f:
    pcode = f.read()

new_param = "    {'id': 'spar_tab_width', 'type': 'float', 'default': '6.0', 'tab': 'Other', 'group': 'Other', 'label': 'Outer Tab Width', 'widget': 'entry'},\n"

pcode = re.sub(r"\]\n\nSINGLE_PARAMS", new_param + "]\n\nSINGLE_PARAMS", pcode)
pcode = re.sub(r"\]\n$", new_param + "]\n", pcode)

with open("ui/param_spec.py", "w") as f:
    f.write(pcode)

print("spar_tab_width added!")
