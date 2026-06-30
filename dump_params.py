import re

with open('ui/batch_mode.py', 'r') as f:
    code = f.read()

# Find all self.var_name = tk.TypeVar(...) 
matches = re.findall(r"self\.([a-zA-Z0-9_]+)\s*=\s*(tk\.[a-zA-Z]+Var|getattr\(self,\s*'[^']+',\s*tk\.[a-zA-Z]+Var)\(.*?(?:value=['\"]?([^'\"]*)['\"]?)?\)", code)

# matches is a list of tuples (var_name, var_type_code, value)
# But `value` is tricky due to the regex.
# Let's write a simpler regex:
matches = re.findall(r"self\.([a-zA-Z0-9_]+)\s*=\s*(?:getattr\(self,\s*'[^']+',\s*)?tk\.(StringVar|BooleanVar|IntVar|DoubleVar)\(\s*(?:value\s*=\s*(.*?))?\)(?:\))?", code)

print(f"Found {len(matches)} variables.")
for var_name, var_type, value in matches:
    if value.startswith("'") or value.startswith('"'):
        value = value[1:-1]
    # some values might be True/False, let's parse them
    if value == "True": value = True
    elif value == "False": value = False
    elif value == "": value = "''"
    
    t = 'str'
    if var_type == 'BooleanVar': t = 'bool'
    elif var_type == 'IntVar': t = 'int'
    # we treat StringVar mostly as float or str. In our spec, we can use float if it defaults to a number.
    if t == 'str' and str(value).replace('.', '').isdigit():
        t = 'float'
    if var_name == "wing_type": t = 'str'
    
    # print dict form
    print(f"    {{'id': '{var_name}', 'type': '{t}', 'default': {repr(value)}, 'tab': 'Unknown', 'group': 'Unknown', 'label': '{var_name}'}},")

