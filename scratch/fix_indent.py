with open('core/export_3d.py', 'r') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if 'if t > 1e-5:' in lines[i] and '                            ' in lines[i]:
        lines[i] = '                            if t > 1e-5:\n'

with open('core/export_3d.py', 'w') as f:
    f.writelines(lines)
print("Fixed indent")
