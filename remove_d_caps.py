import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

code = re.sub(r"    \{'id': 'te_cap_uf_d',.*?\},\n", "", code)
code = re.sub(r"    \{'id': 'te_cap_lf_d',.*?\},\n", "", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Removed te_cap_uf_d and te_cap_lf_d")
