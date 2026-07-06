with open('core/engine.py', 'r') as f:
    content = f.read()

bad = "    file1: str\n    smooth_curves: bool = False\n    file2: str"
good = "    file1: str\n    file2: str"
content = content.replace(bad, good)

# Find the end of RibParameters fields and insert smooth_curves: bool = False
insert_point = "    margin_bolt: float\n"
content = content.replace(insert_point, insert_point + "    smooth_curves: bool = False\n")

with open('core/engine.py', 'w') as f:
    f.write(content)
