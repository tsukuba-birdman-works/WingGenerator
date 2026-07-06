with open('core/engine.py', 'r') as f:
    code = f.read()

# 1. Update export_dxf signature
old_sig = "def export_dxf(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None):"
new_sig = "def export_dxf(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None, jig_pts=None):"
code = code.replace(old_sig, new_sig)

# 2. Add JIG_OUTLINE layer
old_layers1 = "doc.layers.add(name='TE_PART', color=4)"
new_layers1 = "doc.layers.add(name='TE_PART', color=4)\n            doc.layers.add(name='JIG_OUTLINE', color=5)"
code = code.replace(old_layers1, new_layers1)

old_layers2 = "doc.layers.new(name='TE_PART', dxfattribs={'color': 4})"
new_layers2 = "doc.layers.new(name='TE_PART', dxfattribs={'color': 4})\n            doc.layers.new(name='JIG_OUTLINE', dxfattribs={'color': 5})"
code = code.replace(old_layers2, new_layers2)

# 3. Add jig drawing
old_draw = "if len(te_part) > 0: msp.add_lwpolyline(shift_poly(te_part), close=True, dxfattribs={'layer': 'TE_PART'})"
new_draw = old_draw + "\n        if jig_pts is not None and len(jig_pts) > 0: msp.add_lwpolyline(shift_poly(jig_pts), close=True, dxfattribs={'layer': 'JIG_OUTLINE'})"
code = code.replace(old_draw, new_draw)

with open('core/engine.py', 'w') as f:
    f.write(code)
