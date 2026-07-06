import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """    poly = Polygon(pts)
    poly = poly.buffer(0) # Fix self-intersections

    # Create slots"""

code = code.replace(
    '    poly = Polygon(pts)\n\n    # Create slots',
    replacement
)

with open('core/engine.py', 'w') as f: f.write(code)
