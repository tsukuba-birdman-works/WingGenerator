with open('core/engine.py', 'r') as f:
    content = f.read()
if 'smooth_curves: bool = False' not in content:
    content = content.replace("class RibParameters:\n    file1: str", "class RibParameters:\n    file1: str\n    smooth_curves: bool = False")
    with open('core/engine.py', 'w') as f:
        f.write(content)
print("Updated RibParameters in engine.py")
