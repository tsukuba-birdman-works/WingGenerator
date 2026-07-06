import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """    if not te_x_arr:
        # Fallback if empty for some reason
        te_x_arr.append(te_support_start_x)
        te_y_arr.append(te_start_y)
        te_x_arr.append(chord)
        te_y_arr.append(te_start_y)"""

code = code.replace(
    '    for x, y in zip(te_x_arr, te_y_arr):',
    replacement + '\n\n    for x, y in zip(te_x_arr, te_y_arr):'
)

with open('core/engine.py', 'w') as f: f.write(code)
