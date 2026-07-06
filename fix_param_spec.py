import re

with open('ui/param_spec.py', 'r') as f:
    content = f.read()

# Fix connector types
content = content.replace("'values': ['V-Shape', 'Y-Shape']", "'values': ['V-Shape (In-up)', 'V-Shape (In-down)', 'V-Shape (Out-up)', 'V-Shape (Out-down)', 'Y-Shape']")

# Remove local_truss_angle and washout_exp
# We can just comment out or delete the dictionaries for them.
content = re.sub(r"\s*\{'id': 'local_truss_angle'.*?\},", "", content, flags=re.DOTALL)
content = re.sub(r"\s*\{'id': 'washout_exp'.*?\},", "", content, flags=re.DOTALL)

with open('ui/param_spec.py', 'w') as f:
    f.write(content)
