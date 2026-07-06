import re

with open('core/export_dxf.py', 'r') as f:
    code = f.read()

# Fix origin offset for normal ribs
code = re.sub(
    r"origin_offset = \(0, -current_y_offset\) if all_in_one else \(0, 0\)",
    r"origin_offset = (res[1][0], res[1][1] - current_y_offset) if all_in_one else res[1]",
    code
)

# Fix max/min for ribs (they check res[1] which is just a single point (x,y), but len of it is 2 so it doesn't crash here but gives a wrong condition)
code = re.sub(
    r"max_y = get_max_y\(res\[0\]\) if len\(res\[1\]\) > 0 else 50\.0\n(.*?)min_y = get_min_y\(res\[0\]\) if len\(res\[1\]\) > 0 else 0\.0",
    r"max_y = get_max_y(res[0]) if len(res[0]) > 0 else 50.0\n\1min_y = get_min_y(res[0]) if len(res[0]) > 0 else 0.0",
    code
)

# Fix jigs
code = code.replace(
    "origin_offset = (0, -current_y_offset) if all_in_one else (0, 0)",
    "origin_offset = (0, -current_y_offset) if all_in_one else (0, 0)"
)

with open('core/export_dxf.py', 'w') as f:
    f.write(code)

