import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

obsolete = [
    r"\s*\{'id': 'cam_margin'[^}]+\},",
    r"\s*\{'id': 'cam_selected_rib'[^}]+\},",
    r"\s*\{'id': 'tab_depth'[^}]+\},"
]

for obs in obsolete:
    code = re.sub(obs, "", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Obsolete CAM Milling tabs deleted.")
