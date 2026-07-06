import re

with open('core/engine.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_jig = False
for line in lines:
    if line.startswith("def generate_jig_at_y(self"):
        in_jig = True
    
    if in_jig:
        if line.strip() == "":
            new_lines.append("\n")
        else:
            new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open('core/engine.py', 'w') as f:
    f.writelines(new_lines)

