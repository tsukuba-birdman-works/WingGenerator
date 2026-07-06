with open('ui/param_spec.py', 'r') as f:
    content = f.read()

target = "{'id': 'file1_path', 'type': 'str', 'default': '', 'tab': 'Wing', 'group': 'Airfoil (Root)', 'label': 'Airfoil File', 'widget': 'file'},"
new_line = "    {'id': 'smooth_curves', 'type': 'bool', 'default': False, 'tab': 'Wing', 'group': 'Airfoil (Root)', 'label': 'Smooth Curves (Spline Interp)', 'widget': 'checkbutton'},\n"

content = content.replace(target, target + "\n" + new_line)

with open('ui/param_spec.py', 'w') as f:
    f.write(content)
