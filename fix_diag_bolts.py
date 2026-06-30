import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

replacements = {
    # Diag Spars
    'diag1_active': ("'tab': 'Spar'", "'group': 'Diag Spar 1'", "'label': 'Active'"),
    'diag1_y_main': ("'tab': 'Spar'", "'group': 'Diag Spar 1'", "'label': 'Y at Main Spar (mm)'"),
    'diag1_y_rear': ("'tab': 'Spar'", "'group': 'Diag Spar 1'", "'label': 'Y at Rear Spar (mm)'"),
    
    'diag2_active': ("'tab': 'Spar'", "'group': 'Diag Spar 2'", "'label': 'Active'"),
    'diag2_y_main': ("'tab': 'Spar'", "'group': 'Diag Spar 2'", "'label': 'Y at Main Spar (mm)'"),
    'diag2_y_rear': ("'tab': 'Spar'", "'group': 'Diag Spar 2'", "'label': 'Y at Rear Spar (mm)'"),

    # Bolts
    'root_bolt1_dia': ("'tab': 'Spar'", "'group': 'Root Bolt 1'", "'label': 'Dia (mm)'"),
    'root_bolt1_dx': ("'tab': 'Spar'", "'group': 'Root Bolt 1'", "'label': 'Pos dX (mm)'"),
    'root_bolt1_dy': ("'tab': 'Spar'", "'group': 'Root Bolt 1'", "'label': 'Pos dY (mm)'"),

    'root_bolt2_dia': ("'tab': 'Spar'", "'group': 'Root Bolt 2'", "'label': 'Dia (mm)'"),
    'root_bolt2_dx': ("'tab': 'Spar'", "'group': 'Root Bolt 2'", "'label': 'Pos dX (mm)'"),
    'root_bolt2_dy': ("'tab': 'Spar'", "'group': 'Root Bolt 2'", "'label': 'Pos dY (mm)'"),

    'tip_bolt1_dia': ("'tab': 'Spar'", "'group': 'Tip Bolt 1'", "'label': 'Dia (mm)'"),
    'tip_bolt1_dx': ("'tab': 'Spar'", "'group': 'Tip Bolt 1'", "'label': 'Pos dX (mm)'"),
    'tip_bolt1_dy': ("'tab': 'Spar'", "'group': 'Tip Bolt 1'", "'label': 'Pos dY (mm)'"),

    'tip_bolt2_dia': ("'tab': 'Spar'", "'group': 'Tip Bolt 2'", "'label': 'Dia (mm)'"),
    'tip_bolt2_dx': ("'tab': 'Spar'", "'group': 'Tip Bolt 2'", "'label': 'Pos dX (mm)'"),
    'tip_bolt2_dy': ("'tab': 'Spar'", "'group': 'Tip Bolt 2'", "'label': 'Pos dY (mm)'"),
    
    'bolt_spacer_inner_dia': ("'tab': 'Spar'", "'group': 'Bolt Spacers & Margins'", "'label': 'Spacer Inner Dia'"),
    'bolt_spacer_length': ("'tab': 'Spar'", "'group': 'Bolt Spacers & Margins'", "'label': 'Spacer Length'"),
    'margin_bolt': ("'tab': 'Spar'", "'group': 'Bolt Spacers & Margins'", "'label': 'Bolt Margin'"),
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
        new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("Diag spars and bolts updated!")
