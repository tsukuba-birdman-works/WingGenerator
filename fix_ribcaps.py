import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# 1. Update Rib Cap labels and groups, and move to Rib tab
replacements = {
    'rc1_act': ("'tab': 'Rib'", "'group': 'Rib Cap 1'", "'label': 'Active'"),
    'rc1_start': ("'tab': 'Rib'", "'group': 'Rib Cap 1'", "'label': 'Start (%)'"),
    'rc1_end': ("'tab': 'Rib'", "'group': 'Rib Cap 1'", "'label': 'End (%)'"),
    'rc1_width': ("'tab': 'Rib'", "'group': 'Rib Cap 1'", "'label': 'Width (mm)'"),
    'rc1_thick': ("'tab': 'Rib'", "'group': 'Rib Cap 1'", "'label': 'Thickness (mm)'"),
    
    'rc2_act': ("'tab': 'Rib'", "'group': 'Rib Cap 2'", "'label': 'Active'"),
    'rc2_start': ("'tab': 'Rib'", "'group': 'Rib Cap 2'", "'label': 'Start (%)'"),
    'rc2_end': ("'tab': 'Rib'", "'group': 'Rib Cap 2'", "'label': 'End (%)'"),
    'rc2_width': ("'tab': 'Rib'", "'group': 'Rib Cap 2'", "'label': 'Width (mm)'"),
    'rc2_thick': ("'tab': 'Rib'", "'group': 'Rib Cap 2'", "'label': 'Thickness (mm)'"),
}

lines = code.split('\n')
new_lines = []
for line in lines:
    replaced = False
    for k, (t, g, l) in replacements.items():
        if f"'id': '{k}'" in line:
            line = re.sub(r"'tab': '[^']*'", t, line)
            line = re.sub(r"'group': '[^']*'", g, line)
            line = re.sub(r"'label': '[^']*'", l, line)
            new_lines.append(line)
            replaced = True
            break
            
    if not replaced:
        # 2. Move Cross Bracing to Stringer tab
        if "'group': 'Cross Bracing'" in line:
            line = re.sub(r"'tab': '[^']*'", "'tab': 'Stringer'", line)
        new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("Rib caps and Cross Bracing updated!")
