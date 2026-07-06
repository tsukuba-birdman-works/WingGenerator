import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """    if not te_x_arr:
        te_x_arr.append(te_support_start_x)
        te_y_arr.append(te_start_y)
        te_x_arr.append(chord)
        te_y_arr.append(te_start_y)

    last_x = te_x_arr[-1]

    pts = []
    # Bottom edge (left to right)
    pts.append((fm_left, base_y))
    pts.append((last_x, base_y))
    
    # Top edge of TE support (right to left)
    for x, y in zip(reversed(te_x_arr), reversed(te_y_arr)):
        pts.append((x, y))
        
    pts.append((te_x_arr[0], base_y + base_thickness))
    pts.append((rm_right, base_y + base_thickness))
    pts.append((rm_right, rm_top))
    pts.append((rm_left, rm_top))
    pts.append((rm_left, base_y + base_thickness))
    pts.append((fm_right, base_y + base_thickness))
    pts.append((fm_right, fm_top))
    pts.append((fm_left, fm_top))

    try:
        from shapely.validation import make_valid
        poly = make_valid(Polygon(pts))
        if not poly.is_valid:
            poly = poly.buffer(0)
    except:
        poly = Polygon(pts).buffer(0)
        
    # debug print
    if not poly.is_valid:
        print("POLY INVALID. points:")
        for pt in pts: print(pt)"""

code = code.replace(
    '    if not te_x_arr:\n        te_x_arr.append(te_support_start_x)',
    '# START REPLACE'
)

# wait I will just rewrite generate_jig_at_y to use string replace and print the points on error
