with open('core/engine.py', 'r') as f:
    content = f.read()

content = content.replace("    smooth_curves: bool = False\n", "")

# Find the end of RibParameters fields which is right before `    def from_dict` or similar
insert_point = "    fast_mode: bool = False\n"
content = content.replace(insert_point, insert_point + "    smooth_curves: bool = False\n")

with open('core/engine.py', 'w') as f:
    f.write(content)
