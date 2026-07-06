import re

with open('ui/param_spec.py', 'r') as f:
    content = f.read()

for i in range(1, 5):
    old_type = re.search(r"\{'id': 'conn" + str(i) + r"_type'.*?\}", content)
    old_y = re.search(r"\{'id': 'conn" + str(i) + r"_y'.*?\}", content)
    if old_type:
        new_type = f"{{'id': 'conn{i}_type', 'type': 'str', 'default': 'V-Shape', 'tab': 'Brace & Connector', 'group': 'Connectors', 'label': 'Conn {i} Type', 'widget': 'combobox', 'values': ['V-Shape', 'Y-Shape']}}"
        content = content.replace(old_type.group(0), new_type)
    if old_y:
        new_y = f"{{'id': 'conn{i}_y', 'type': 'float', 'default': 0.0, 'tab': 'Brace & Connector', 'group': 'Connectors', 'label': 'Conn {i} Y (mm)', 'widget': 'entry'}}"
        content = content.replace(old_y.group(0), new_y)

with open('ui/param_spec.py', 'w') as f:
    f.write(content)
