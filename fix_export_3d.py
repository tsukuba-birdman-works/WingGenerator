with open('core/export_3d.py', 'r') as f:
    content = f.read()

content = content.replace('("In=Up" in conn_type)', '("In=Up" in conn_type or "In-up" in conn_type or "Out-down" in conn_type)')

with open('core/export_3d.py', 'w') as f:
    f.write(content)
