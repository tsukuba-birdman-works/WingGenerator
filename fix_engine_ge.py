import re

with open('core/engine.py', 'r') as f:
    text = f.read()

replacements = [
    ("if front_dia > 0:", "if front_dia >= 0:"),
    ("if rear_dia > 0:", "if rear_dia >= 0:"),
    ("if spar_hole_dia > 0:", "if spar_hole_dia >= 0:"),
    ("if bolt1_dia > 0:", "if bolt1_dia >= 0:"),
    ("if bolt2_dia > 0:", "if bolt2_dia >= 0:"),
    ("if x_dia > 0:", "if x_dia >= 0:"),
    ("if d_m > 0:", "if d_m >= 0:"),
    ("if d_f > 0:", "if d_f >= 0:"),
    ("if d_r > 0:", "if d_r >= 0:"),
    ("if d_b1 > 0:", "if d_b1 >= 0:"),
    ("if d_b2 > 0:", "if d_b2 >= 0:"),
    ("if spar_hole_dv > 0 else dh", "if spar_hole_dv >= 0 else dh"),
    ("if spar_hole_dv > 0 else dh_prot", "if spar_hole_dv >= 0 else dh_prot"),
    ("if dv_m > 0 else d_m", "if dv_m >= 0 else d_m"),
    ("if spar_hole_dia > 0 else []", "if spar_hole_dia >= 0 else []"),
    ("if rear_dia > 0 else []", "if rear_dia >= 0 else []"),
    ("if front_dia > 0 else []", "if front_dia >= 0 else []"),
    ("if bolt1_dia > 0 else []", "if bolt1_dia >= 0 else []"),
    ("if bolt2_dia > 0 else []", "if bolt2_dia >= 0 else []"),
    ("d_f > 0 else (c_m[0]", "d_f >= 0 else (c_m[0]")
]

for t, r in replacements:
    text = text.replace(t, r)

with open('core/engine.py', 'w') as f:
    f.write(text)

