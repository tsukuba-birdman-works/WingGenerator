import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

replacements = {
    # Front Spar
    'front_spar_dia': ("'tab': 'Spar'", "'group': 'Front Spar'", "'label': 'Outer Dia (mm)'"),
    'front_spar_inner_dia': ("'tab': 'Spar'", "'group': 'Front Spar'", "'label': 'Inner Dia (mm)'"),
    'front_spar_dx': ("'tab': 'Spar'", "'group': 'Front Spar'", "'label': 'Pos dX (mm)'"),
    'front_spar_dy': ("'tab': 'Spar'", "'group': 'Front Spar'", "'label': 'Pos dY (mm)'"),
    
    # Rear Spar
    'rear_spar_dia': ("'tab': 'Spar'", "'group': 'Rear Spar'", "'label': 'Outer Dia (mm)'"),
    'rear_spar_inner_dia': ("'tab': 'Spar'", "'group': 'Rear Spar'", "'label': 'Inner Dia (mm)'"),
    'rear_spar_dx': ("'tab': 'Spar'", "'group': 'Rear Spar'", "'label': 'Pos dX (mm)'"),
    'rear_spar_dy': ("'tab': 'Spar'", "'group': 'Rear Spar'", "'label': 'Pos dY (mm)'"),
    
    # Main Spar
    'spar_hole_dia': ("'tab': 'Spar'", "'group': 'Main Spar'", "'label': 'Outer Dia (mm)'"),
    'main_spar_inner_dia': ("'tab': 'Spar'", "'group': 'Main Spar'", "'label': 'Inner Dia (mm)'"),
    
    # CNC Tabs
    'fr_spar_tab_dist': ("'tab': 'CNC'", "'group': 'Spar Tabs'", "'label': 'F/R Tab Dist (mm)'"),
    'fr_spar_tab_width': ("'tab': 'CNC'", "'group': 'Spar Tabs'", "'label': 'F/R Tab Width (mm)'"),
    'main_spar_tab_dist': ("'tab': 'CNC'", "'group': 'Spar Tabs'", "'label': 'Main Tab Dist (mm)'"),
    'main_spar_tab_width': ("'tab': 'CNC'", "'group': 'Spar Tabs'", "'label': 'Main Tab Width (mm)'"),
    
    # CNC General
    'cam_margin': ("'tab': 'CNC'", "'group': 'CAM Milling'", "'label': 'CAM Margin (mm)'"),
    'cam_selected_rib': ("'tab': 'CNC'", "'group': 'CAM Milling'", "'label': 'Selected Rib'"),
    'tab_depth': ("'tab': 'CNC'", "'group': 'CAM Milling'", "'label': 'Tab Depth (mm)'"),
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

print("Spar and CNC parameters updated!")
