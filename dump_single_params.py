import re

with open('ui/single_mode.py', 'r') as f:
    code = f.read()

matches = re.findall(r"self\.([a-zA-Z0-9_]+)\s*=\s*(?:getattr\(self,\s*'[^']+',\s*)?tk\.(StringVar|BooleanVar|IntVar|DoubleVar)\(\s*(?:value\s*=\s*(.*?))?\)(?:\))?", code)

print(f"Found {len(matches)} variables in single_mode.")
