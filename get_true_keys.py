import re

with open('backup_batch_mode.py', 'r') as f:
    code = f.read()

# Extract get_all_vars dict
match = re.search(r'def get_all_vars\(self\):\s*v = \{(.*?)\}', code, re.DOTALL)
if match:
    dict_content = match.group(1)
    keys = re.findall(r"'([a-zA-Z0-9_]+)':", dict_content)
    
    # Let's map these true keys into BATCH_PARAMS
    # I will read the existing ui/param_spec.py, and if a key is missing, add it with type float/bool/str
    import ast
    try:
        with open('ui/param_spec.py', 'r') as f:
            spec_code = f.read()
        lines = []
        for line in spec_code.split('\n'):
            if line.strip().startswith("{'id':"):
                lines.append(line.strip().rstrip(','))
        existing_params = [ast.literal_eval(l) for l in lines]
    except Exception as e:
        print("Error reading param_spec:", e)
        existing_params = []
        
    existing_keys = {p['id'] for p in existing_params}
    
    for key in keys:
        if key not in existing_keys:
            # guess type
            t = 'float'
            w = 'entry'
            if 'export_' in key or 'act' in key: t = 'bool'; w = 'checkbutton'
            if 'mat_' in key or 'type' in key or 'path' in key: t = 'str'; w = 'entry'
            
            p = {'id': key, 'type': t, 'default': '' if t=='str' else (False if t=='bool' else 0.0), 'tab': 'Missing', 'group': 'Missing', 'label': key, 'widget': w}
            existing_params.append(p)
            
    with open('ui/param_spec.py', 'w') as f:
        f.write("BATCH_PARAMS = [\n")
        for p in existing_params:
            f.write(f"    {repr(p)},\n")
        f.write("]\n")
    print(f"Total parameters: {len(existing_params)}")
