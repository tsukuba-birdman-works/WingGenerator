import re

with open('ui/param_spec.py', 'r') as f:
    text = f.read()

# Delete the old dx/dy for rear_spar
text = re.sub(r"\s*\{'id': 'rear_spar_dx',.*?\},", "", text, flags=re.DOTALL)
text = re.sub(r"\s*\{'id': 'rear_spar_dy',.*?\},", "", text, flags=re.DOTALL)

# Also rename the group of the first two (dia and inner_dia) to Rear Spar (Root)
text = re.sub(r"('id': 'rear_spar_dia',.*?group': )'Rear Spar'", r"\1'Rear Spar (Root)'", text)
text = re.sub(r"('id': 'rear_spar_inner_dia',.*?group': )'Rear Spar'", r"\1'Rear Spar (Root)'", text)

# Add the new parameters right after rear_spar_inner_dia
new_params = """
    {'id': 'rear_spar_dx_root', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Pos dX Root (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dy_root', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Root)', 'label': 'Pos dY Root (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dx_tip', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Tip)', 'label': 'Pos dX Tip (mm)', 'widget': 'entry'},
    {'id': 'rear_spar_dy_tip', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Rear Spar (Tip)', 'label': 'Pos dY Tip (mm)', 'widget': 'entry'},"""

text = re.sub(r"(\{'id': 'rear_spar_inner_dia',.*?\},\n)", r"\1" + new_params + "\n", text, flags=re.DOTALL)

with open('ui/param_spec.py', 'w') as f:
    f.write(text)

