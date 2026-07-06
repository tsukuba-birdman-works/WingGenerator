import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """        if not doc.layers.has_entry('PART'):
            doc.layers.add(name='PART', color=7)"""

code = code.replace(
    "        if 'PART' not in doc.layers:\n            doc.layers.add(name='PART', color=7)",
    replacement
)

with open('core/engine.py', 'w') as f: f.write(code)
