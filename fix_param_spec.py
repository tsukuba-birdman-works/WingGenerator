with open('ui/param_spec.py', 'r') as f:
    text = f.read()

# Replace rear_spar_dx and rear_spar_dy with root and tip variants
old_rear = """    {'id': 'rear_spar_dia', 'type': 'float', 'default': '11.4', 'tab': 'Spar', 'group': 'Rear Spar', 'label': 'Outer Dia (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_inner_dia', 'type': 'float', 'default': '10.0', 'tab': 'Spar', 'group': 'Rear Spar', 'label': 'Inner Dia (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dx', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar', 'label': 'Pos dX (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dy', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar', 'label': 'Pos dY (mm)', 'widget': 'entry'},"""

new_rear = """    {'id': 'rear_spar_dia', 'type': 'float', 'default': '11.4', 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Outer Dia (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_inner_dia', 'type': 'float', 'default': '10.0', 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Inner Dia (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dx_root', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Pos dX Root (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dy_root', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Pos dY Root (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dx_tip', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Tip)', 'label': 'Pos dX Tip (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dy_tip', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Tip)', 'label': 'Pos dY Tip (mm)', 'widget': 'entry'},"""

if "rear_spar_dx_root" not in text:
    text = text.replace(old_rear, new_rear)
    with open('ui/param_spec.py', 'w') as f:
        f.write(text)
        print("Replaced successfully")
else:
    print("Already updated")
