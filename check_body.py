with open('core/engine.py') as f:
    lines = f.readlines()
start = -1
for i, l in enumerate(lines):
    if "def export_single_poly_dxf" in l:
        start = i
        break
for i in range(start, start + 30):
    print(lines[i], end="")
