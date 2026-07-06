import re

with open('ui/param_spec.py', 'r') as f: code = f.read()

target = r"    # DXF Layer Names.*?widget': 'entry'\},"
code = re.sub(target, "", code, flags=re.DOTALL)

with open('ui/param_spec.py', 'w') as f: f.write(code)
