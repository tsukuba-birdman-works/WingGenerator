import re

with open('recovered_jig.py', 'r') as f:
    orig = f.read()

# Fix 1: change slot centers
orig = orig.replace(
    "slot1_x = c_m[0] - slot_interval / 2.0\n        slot2_x = c_m[0] + slot_interval / 2.0",
    "c_tip = float(p.get('chord_tip', 200.0)) / 2.0\n        slot1_x = c_tip - slot_interval / 2.0\n        slot2_x = c_tip + slot_interval / 2.0"
)

# Fix 2: Move te_pad union to BEFORE the wing difference, and add protection to wing_poly
# Originally:
#         wing_poly = Polygon(...)
#         frame = frame.difference(wing_poly.buffer(1.0).buffer(0))
#         [te_pad code]
#         frame = frame.union(te_pad)

old_wing_subtraction = """        # Subtract the whole wing profile so nothing enters the wing (except TE pad below)
        wing_poly = Polygon(np.column_stack((np.concatenate((u_x, l_x)), np.concatenate((u_y, l_y)))))
        frame = frame.difference(wing_poly.buffer(1.0).buffer(0)) # Add 1mm tolerance so it doesn't rub the skin"""

new_wing_subtraction = """        # First add the precise TE support pad
        te_x_arr, te_y_arr = [], []
        for xi, yi in zip(l_x, l_y):
            if te_support_start_x <= xi <= te_support_end_x:
                te_x_arr.append(xi)
                te_y_arr.append(yi)
        if len(te_x_arr) >= 2:
            te_pad_pts = [(te_support_start_x, te_y_arr[0] - 10.0)]
            te_pad_pts.extend(list(zip(te_x_arr, te_y_arr)))
            te_pad_pts.append((te_support_end_x, te_y_arr[-1] - 10.0))
            te_pad_pts.append((te_support_start_x, te_y_arr[0] - 10.0)) # Close
            te_pad = Polygon(te_pad_pts).buffer(0)
            frame = frame.union(te_pad)

        # Then subtract the whole wing profile so nothing enters the wing
        # EXCEPT we protect the spar areas so the pillars can reach the spars!
        wing_poly = Polygon(np.column_stack((np.concatenate((u_x, l_x)), np.concatenate((u_y, l_y)))))
        wing_cut_tool = wing_poly.buffer(1.0).buffer(0)
        
        # Protect spar regions
        protected_boxes = []
        if d_m > 0: protected_boxes.append(box(c_m[0] - d_m/2.0 - 5.0, -1000, c_m[0] + d_m/2.0 + 5.0, 1000))
        if d_f > 0: protected_boxes.append(box(c_f[0] - d_f/2.0 - 5.0, -1000, c_f[0] + d_f/2.0 + 5.0, 1000))
        if d_r > 0: protected_boxes.append(box(c_r[0] - d_r/2.0 - 5.0, -1000, c_r[0] + d_r/2.0 + 5.0, 1000))
        
        if protected_boxes:
            wing_cut_tool = wing_cut_tool.difference(unary_union(protected_boxes))
            
        frame = frame.difference(wing_cut_tool)"""

orig = orig.replace(old_wing_subtraction, new_wing_subtraction)

old_te_pad = """        # Also need to add the precise TE support pad
        te_x_arr, te_y_arr = [], []
        for xi, yi in zip(l_x, l_y):
            if te_support_start_x <= xi <= te_support_end_x:
                te_x_arr.append(xi)
                te_y_arr.append(yi)
        if len(te_x_arr) >= 2:
            te_pad_pts = [(te_support_start_x, te_y_arr[0] - 10.0)]
            te_pad_pts.extend(list(zip(te_x_arr, te_y_arr)))
            te_pad_pts.append((te_support_end_x, te_y_arr[-1] - 10.0))
            te_pad_pts.append((te_support_start_x, te_y_arr[0] - 10.0)) # Close
            te_pad = Polygon(te_pad_pts).buffer(0)
            frame = frame.union(te_pad)"""

orig = orig.replace(old_te_pad, "")

# Fix 3: U-shaped cut -> 60% box cut
old_spar_cut = """        # Cut spar holes (U shaped)
        if d_f > 0:
            f_hole = Point(c_f).buffer(d_f/2.0)
            f_cut = box(c_f[0] - d_f, c_f[1], c_f[0] + d_f, c_f[1] + d_f)
            frame = frame.difference(f_hole.union(f_cut))

        if d_m > 0:
            m_hole = Point(c_m).buffer(d_m/2.0)
            m_cut = box(c_m[0] - d_m, c_m[1], c_m[0] + d_m, c_m[1] + d_m)
            frame = frame.difference(m_hole.union(m_cut))

        if d_r > 0:
            r_hole = Point(c_r).buffer(d_r/2.0)
            r_cut = box(c_r[0] - d_r, c_r[1], c_r[0] + d_r, c_r[1] + d_r)
            frame = frame.difference(r_hole.union(r_cut))"""

new_spar_cut = """        # Cut spar holes (60% box shaped)
        if d_f > 0:
            bw = 0.6 * d_f
            f_cut = box(c_f[0] - bw/2.0, c_f[1] - d_f/2.0, c_f[0] + bw/2.0, c_f[1] + d_f)
            frame = frame.difference(f_cut)

        if d_m > 0:
            bw = 0.6 * d_m
            m_cut = box(c_m[0] - bw/2.0, c_m[1] - d_m/2.0, c_m[0] + bw/2.0, c_m[1] + d_m)
            frame = frame.difference(m_cut)

        if d_r > 0:
            bw = 0.6 * d_r
            r_cut = box(c_r[0] - bw/2.0, c_r[1] - d_r/2.0, c_r[0] + bw/2.0, c_r[1] + d_r)
            frame = frame.difference(r_cut)"""

orig = orig.replace(old_spar_cut, new_spar_cut)

# Now we have the patched generate_jig_at_y.
# Let's write it to a temp file
with open('patch_jig_temp.py', 'w') as f:
    f.write(orig)

