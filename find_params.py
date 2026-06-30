import re

all_vars = set()

# Scan param_spec.py
with open("ui/param_spec.py", "r") as f:
    spec = f.read()
for m in re.finditer(r"'id': '([^']+)'", spec):
    all_vars.add(m.group(1))

# Scan manual UI vars in base_mode.py
with open("ui/base_mode.py", "r") as f:
    base = f.read()
for m in re.finditer(r"self\.([a-zA-Z0-9_]+)\s*=\s*tk\.(?:StringVar|BooleanVar|DoubleVar|IntVar)", base):
    all_vars.add(m.group(1))

# Scan core/engine.py and core/cam_engine.py for parameter accesses
accessed = set()
for file in ["core/engine.py", "core/cam_engine.py"]:
    with open(file, "r") as f:
        code = f.read()
    
    # p['something']
    for m in re.finditer(r"p(?:arams)?\['([^']+)'\]", code):
        accessed.add(m.group(1))
    
    # p.get('something')
    for m in re.finditer(r"p(?:arams)?\.get\('([^']+)'", code):
        accessed.add(m.group(1))

# Now find what is accessed but not defined in UI
missing = accessed - all_vars

print("Variables accessed in engine but missing from UI definitions:")
for v in sorted(list(missing)):
    print("- " + v)

