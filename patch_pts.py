import re
with open('core/engine.py', 'r') as f: code = f.read()

jig_old = """    pts = [
        (fm_left, base_y),
        (rm_right, base_y),
        (rm_right, rm_top),
        (rm_left, rm_top),
        (rm_left, base_y + base_thickness),
        (fm_right, base_y + base_thickness),
        (fm_right, fm_top),
        (fm_left, fm_top)
    ]

    # Trace the airfoil TE
    te_x_arr = []
    te_y_arr = []
    for i in range(len(l_x)):
        if l_x[i] >= te_support_start_x and l_x[i] <= chord:
            te_x_arr.append(l_x[i])
            te_y_arr.append(l_y[i])

    if not te_x_arr:
        # Fallback if empty for some reason
        te_x_arr.append(te_support_start_x)
        te_y_arr.append(te_start_y)
        te_x_arr.append(chord)
        te_y_arr.append(te_start_y)

    for x, y in zip(te_x_arr, te_y_arr):
        pts.append((x, y))

    # Ensure it ends at exactly 'chord' or the last point
    last_x, last_y = te_x_arr[-1], te_y_arr[-1]
    
    pts.append((last_x, base_y))
    pts.append((fm_left, base_y))  # close the loop"""

jig_new = """    # Trace the airfoil TE
    te_x_arr = []
    te_y_arr = []
    for i in range(len(l_x)):
        if l_x[i] >= te_support_start_x and l_x[i] <= chord:
            te_x_arr.append(l_x[i])
            te_y_arr.append(l_y[i])

    if not te_x_arr:
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
    pts.append((fm_left, fm_top))"""

code = code.replace(jig_old, jig_new)

with open('core/engine.py', 'w') as f: f.write(code)
