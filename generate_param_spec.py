import json

lines = []
with open('raw_params.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith("{'id':"):
            lines.append(line)

# Let's create a template param_spec.py
spec = """
# ui/param_spec.py
# Centralized definition for UI parameters

BATCH_PARAMS = [
"""
spec += "\n".join(lines)
spec += "\n]\n"

with open('ui/param_spec.py', 'w') as f:
    f.write(spec)
print("Generated ui/param_spec.py")
