import sys
with open('core/engine.py', 'r') as f:
    lines = f.readlines()

with open('patch_jig_temp.py', 'r') as f:
    new_func = f.read()

idx0 = -1
for i, l in enumerate(lines):
    if l.startswith("    def generate_jig_at_y("):
        idx0 = i
        break

idx1 = -1
for i, l in enumerate(lines):
    if l.startswith("    def export_dxf("):
        idx1 = i
        break

if idx0 != -1 and idx1 != -1 and idx0 < idx1:
    new_lines = lines[:idx0] + [new_func, "\n"] + lines[idx1:]
    with open('core/engine.py', 'w') as f:
        f.writelines(new_lines)
    print("Injected successfully!")
else:
    print(f"Failed to find indices: idx0={idx0}, idx1={idx1}")
