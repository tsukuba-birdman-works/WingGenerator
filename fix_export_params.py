import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# 1. Remove plank_thick_tip and plank_angle_offset
code = re.sub(r"    \{'id': 'plank_thick_tip',.*?\},\n", "", code)
code = re.sub(r"    \{'id': 'plank_angle_offset',.*?\},\n", "", code)

# 2. Process line by line for the export and material variables
lines = code.split('\n')
new_lines = []
for line in lines:
    if "'id': " not in line:
        new_lines.append(line)
        continue
        
    id_match = re.search(r"'id': '([^']+)'", line)
    if not id_match:
        new_lines.append(line)
        continue
        
    param_id = id_match.group(1)
    
    # Material variables to Export3D > Materials
    if param_id.startswith("mat_"):
        line = re.sub(r"'tab': '[^']*'", "'tab': 'Export3D'", line)
        line = re.sub(r"'group': '[^']*'", "'group': 'Materials'", line)
        # Fix label to be capitalized without 'mat_'
        label_val = param_id.replace('mat_', '').replace('_', ' ').title()
        line = re.sub(r"'label': '[^']*'", f"'label': '{label_val}'", line)
        
    # 3D Export boolean variables to Export3D > Parts Output
    elif param_id.startswith("export_") and param_id != "export_is_left":
        line = re.sub(r"'tab': '[^']*'", "'tab': 'Export3D'", line)
        line = re.sub(r"'group': '[^']*'", "'group': 'Parts Output'", line)
        label_val = param_id.replace('export_', '').replace('_', ' ').title()
        line = re.sub(r"'label': '[^']*'", f"'label': '{label_val}'", line)
        
    # DXF Export layer name variables to DXF > Layer Names
    elif param_id.startswith("dxf_export_"):
        line = re.sub(r"'tab': '[^']*'", "'tab': 'DXF'", line)
        line = re.sub(r"'group': '[^']*'", "'group': 'Layer Names'", line)
        label_val = param_id.replace('dxf_export_', '').replace('_', ' ').title()
        line = re.sub(r"'label': '[^']*'", f"'label': '{label_val}'", line)
        
    new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("Export and material parameters moved and labeled successfully!")
