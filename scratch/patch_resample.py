import re

with open('core/engine.py', 'r') as f:
    content = f.read()

old_code = "        target_distances = np.linspace(0, distances[-1], target_count)"
new_code = """        v1 = np.linspace(0, np.pi, target_count // 2)
        d1 = 0.5 * (1 - np.cos(v1))
        v2 = np.linspace(0, np.pi, target_count - len(v1) + 1)[1:]
        d2 = 0.5 + 0.5 * (1 - np.cos(v2))
        rel_dist = np.concatenate([d1, d2])
        target_distances = rel_dist * distances[-1]"""

content = content.replace(old_code, new_code)

with open('core/engine.py', 'w') as f:
    f.write(content)

with open('core/fin_engine.py', 'r') as f:
    content = f.read()

content = content.replace(old_code, new_code)

with open('core/fin_engine.py', 'w') as f:
    f.write(content)

print("Updated resample_airfoil in engine.py and fin_engine.py")
