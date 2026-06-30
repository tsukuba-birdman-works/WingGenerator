import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

obsolete = [
    r"\s*\{'id': 'main_spar_tab_dist'[^}]+\},",
    r"\s*\{'id': 'main_spar_tab_width'[^}]+\},",
    r"\s*\{'id': 'fr_spar_tab_dist'[^}]+\},",
    r"\s*\{'id': 'fr_spar_tab_width'[^}]+\},"
]

for obs in obsolete:
    code = re.sub(obs, "", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Obsolete CNC tabs deleted.")
