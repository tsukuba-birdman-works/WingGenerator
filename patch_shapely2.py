import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """    try:
        from shapely.validation import make_valid
        poly = make_valid(Polygon(pts))
    except ImportError:
        poly = Polygon(pts).buffer(0)"""

code = code.replace(
    '    poly = Polygon(pts)\n    poly = poly.buffer(0) # Fix self-intersections',
    replacement
)

with open('core/engine.py', 'w') as f: f.write(code)
