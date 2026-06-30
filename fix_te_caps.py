import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# Map specific variables to new groups and simpler labels
replacements = {
    'te_cut': ("'group': 'TE Cut & Thick'", "'label': 'Cut from TE Edge (mm)'"),
    'te_cap_thick': ("'group': 'TE Cut & Thick'", "'label': 'Carbon Cap Thick (mm)'"),
    
    'te_cap_uf_act': ("'group': 'Upper Front Cap'", "'label': 'Active'"),
    'te_cap_uf_w': ("'group': 'Upper Front Cap'", "'label': 'Width'"),
    'te_cap_uf_d': ("'group': 'Upper Front Cap'", "'label': 'Depth (Double)'"),
    
    'te_cap_lf_act': ("'group': 'Lower Front Cap'", "'label': 'Active'"),
    'te_cap_lf_w': ("'group': 'Lower Front Cap'", "'label': 'Width'"),
    'te_cap_lf_d': ("'group': 'Lower Front Cap'", "'label': 'Depth (Double)'"),
    
    'te_cap_ur_act': ("'group': 'Upper Rear Cap'", "'label': 'Active'"),
    'te_cap_ur_w': ("'group': 'Upper Rear Cap'", "'label': 'Width'"),
    
    'te_cap_lr_act': ("'group': 'Lower Rear Cap'", "'label': 'Active'"),
    'te_cap_lr_w': ("'group': 'Lower Rear Cap'", "'label': 'Width'"),
}

lines = code.split('\n')
new_lines = []
for line in lines:
    replaced = False
    for k, (g, l) in replacements.items():
        if f"'id': '{k}'" in line:
            line = re.sub(r"'group': '[^']*'", g, line)
            line = re.sub(r"'label': '[^']*'", l, line)
            new_lines.append(line)
            replaced = True
            break
    if not replaced:
        new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("TE Caps grouped and labeled successfully!")
