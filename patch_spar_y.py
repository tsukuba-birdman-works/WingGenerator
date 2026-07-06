import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """        # Find front spar center
        spar_x = chord * spar_pct / 100.0
        # Line intersecting the airfoil
        spar_y = (np.interp(spar_x, u_x, u_y) + np.interp(spar_x, l_x, l_y)) / 2.0

        # Find rear spar center
        rear_spar_x = chord * float(p.get('rear_spar_dx', 70.0)) / 100.0
        rear_spar_y = (np.interp(rear_spar_x, u_x, u_y) + np.interp(rear_spar_x, l_x, l_y)) / 2.0"""

code = code.replace(
    """        # Find front spar center
        spar_x = chord * spar_pct / 100.0
        # Line intersecting the airfoil
        spar_y_pt = self.find_intersection(spar_x, 0, 90, l_x, l_y, "up")
        spar_y = spar_y_pt[1] if spar_y_pt else 0.0

        # Find rear spar center
        rear_spar_x = chord * p.get('rear_spar_dx', 70.0) / 100.0
        rear_spar_y_pt = self.find_intersection(rear_spar_x, 0, 90, l_x, l_y, "up")
        rear_spar_y = rear_spar_y_pt[1] if rear_spar_y_pt else 0.0""",
    replacement
)

with open('core/engine.py', 'w') as f: f.write(code)
