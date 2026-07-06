import re
with open('ui/batch_mode.py', 'r') as f: code = f.read()

replacement = """        target = self.pm.vars.get('foam_target', tk.StringVar(value="Plank")).get()"""

code = code.replace(
    "        target = self.foam_target.get()",
    replacement
)

with open('ui/batch_mode.py', 'w') as f: f.write(code)
