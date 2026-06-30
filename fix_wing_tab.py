import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# 1. Remove washout_exp and rib_sections
code = re.sub(r"    \{'id': 'washout_exp',.*?\},\n", "", code)
code = re.sub(r"    \{'id': 'rib_sections',.*?\},\n", "", code)

# 2. Reorganize Wing Tab
replacements = {
    'file1_path': ("'tab': 'Wing'", "'group': 'Airfoil (Root)'", "'widget': 'file'", "'label': 'Airfoil File'"),
    'chord_root': ("'tab': 'Wing'", "'group': 'Airfoil (Root)'", "'widget': 'entry'", "'label': 'Chord Length'"),
    'washout_root': ("'tab': 'Wing'", "'group': 'Airfoil (Root)'", "'widget': 'entry'", "'label': 'Washout (deg)'"),
    'spar_pos_root': ("'tab': 'Wing'", "'group': 'Airfoil (Root)'", "'widget': 'entry'", "'label': 'Spar Pos (%)'"),
    
    'file2_path': ("'tab': 'Wing'", "'group': 'Airfoil (Tip)'", "'widget': 'file'", "'label': 'Airfoil File'"),
    'chord_tip': ("'tab': 'Wing'", "'group': 'Airfoil (Tip)'", "'widget': 'entry'", "'label': 'Chord Length'"),
    'washout_tip': ("'tab': 'Wing'", "'group': 'Airfoil (Tip)'", "'widget': 'entry'", "'label': 'Washout (deg)'"),
    'spar_pos_tip': ("'tab': 'Wing'", "'group': 'Airfoil (Tip)'", "'widget': 'entry'", "'label': 'Spar Pos (%)'"),
    
    'wing_span': ("'tab': 'Wing'", "'group': 'Layout'", "'widget': 'entry'", "'label': 'Wing Span'"),
    'joint_length': ("'tab': 'Wing'", "'group': 'Layout'", "'widget': 'entry'", "'label': 'Joint Length'"),
    'rib_interval': ("'tab': 'Wing'", "'group': 'Layout'", "'widget': 'entry'", "'label': 'Rib Interval'"),
    'export_is_left': ("'tab': 'Wing'", "'group': 'Layout'", "'widget': 'checkbutton'", "'label': 'Export as Left Wing'"),
    'wing_type': ("'tab': 'Wing'", "'group': 'Layout'", "'widget': 'combobox', 'values': ['Linear']", "'label': 'Wing Type'")
}

lines = code.split('\n')
new_lines = []
for line in lines:
    replaced = False
    for k, (t, g, w, l) in replacements.items():
        if f"'id': '{k}'" in line:
            # Replace tab
            line = re.sub(r"'tab': '[^']*'", t, line)
            # Replace group
            line = re.sub(r"'group': '[^']*'", g, line)
            # Replace widget (only if it doesn't already have 'values')
            if 'values' in w:
                widget_part = w.split(", ")[0]
                values_part = w.split(", ")[1]
                line = re.sub(r"'widget': '[^']*'", f"{widget_part}, {values_part}", line)
            else:
                line = re.sub(r"'widget': '[^']*'", w, line)
            # Replace label
            line = re.sub(r"'label': '[^']*'", l, line)
            new_lines.append(line)
            replaced = True
            break
    if not replaced:
        new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("Wing tab reorganized successfully!")
