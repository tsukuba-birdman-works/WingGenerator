with open('core/engine.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[925:950]):
    print(f"{i+925}: {line.strip()}")
