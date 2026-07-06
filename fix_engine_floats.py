with open('core/engine.py', 'r') as f:
    orig = f.read()

import re
old_vars = """        te_cut = p.get('te_cut', 0.0)
        d_m = p.get('spar_hole_dia', 0.0)
        d_r = p.get('rear_spar_dia', 0.0)
        d_f = p.get('front_spar_dia', 0.0)

        front_dx = p.get('front_spar_dx', 0.0)
        front_dy = p.get('front_spar_dy', 0.0)
        rear_dx = p.get('rear_spar_dx', 0.0)
        rear_dy = p.get('rear_spar_dy', 0.0)"""

new_vars = """        te_cut = float(p.get('te_cut', 0.0))
        d_m = float(p.get('spar_hole_dia', 0.0))
        d_r = float(p.get('rear_spar_dia', 0.0))
        d_f = float(p.get('front_spar_dia', 0.0))

        front_dx = float(p.get('front_spar_dx', 0.0))
        front_dy = float(p.get('front_spar_dy', 0.0))
        rear_dx = float(p.get('rear_spar_dx', 0.0))
        rear_dy = float(p.get('rear_spar_dy', 0.0))"""

orig = orig.replace(old_vars, new_vars)

old_base_height = "        base_height = p.get('jig_base_height', 100.0)"
new_base_height = "        base_height = float(p.get('jig_base_height', 100.0))"
orig = orig.replace(old_base_height, new_base_height)

old_slot_interval = "        slot_interval = p.get('jig_slot_interval', 100.0)"
new_slot_interval = "        slot_interval = float(p.get('jig_slot_interval', 100.0))"
orig = orig.replace(old_slot_interval, new_slot_interval)

old_slot_width = "        slot_width = p.get('jig_slot_width', 3.0)"
new_slot_width = "        slot_width = float(p.get('jig_slot_width', 3.0))"
orig = orig.replace(old_slot_width, new_slot_width)

old_slot_depth = "        slot_depth = p.get('jig_slot_depth', 10.0)"
new_slot_depth = "        slot_depth = float(p.get('jig_slot_depth', 10.0))"
orig = orig.replace(old_slot_depth, new_slot_depth)

with open('core/engine.py', 'w') as f:
    f.write(orig)

print("Done")
