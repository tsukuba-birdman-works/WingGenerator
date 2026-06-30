import re

with open("ui/param_spec.py", "r") as f:
    pcode = f.read()

# Remove the spar_tab_width parameter completely
pcode = re.sub(r"\s*\{'id': 'spar_tab_width'[^}]+\},", "", pcode)

with open("ui/param_spec.py", "w") as f:
    f.write(pcode)

print("spar_tab_width removed from UI!")
