import re

with open('core/engine.py', 'r') as f:
    code = f.read()

jig_old = """    # Get the airfoil coordinates
    try:
        raw_curve = self.get_slice_curve(self.x_all, self.y_all, self.s_all, 100, 100, t, t)
        pts = self.resample_airfoil(raw_curve, 300)
        u_x, u_y, l_x, l_y = self.split_airfoil(pts)
    except Exception as e:
        print(f"Jig generation error at Y={y_local}: {e}")
        return None"""

jig_new = """    # Get the airfoil coordinates
    try:
        pts1 = self.load_dat(p['file1'])
        pts2 = self.load_dat(p['file2'])
        pts1 = self.resample_airfoil(pts1, 300)
        pts2 = self.resample_airfoil(pts2, 300)
        blend_ratio = t # Using t as blend_ratio from wing_span
        raw_curve = []
        for i in range(min(len(pts1), len(pts2))):
            cx = pts1[i][0] * (1 - blend_ratio) + pts2[i][0] * blend_ratio
            cy = pts1[i][1] * (1 - blend_ratio) + pts2[i][1] * blend_ratio
            raw_curve.append((cx, cy))
        u_x, u_y, l_x, l_y = self.split_airfoil(raw_curve)
    except Exception as e:
        print(f"Jig generation error at Y={y_local}: {e}")
        return None"""

code = code.replace(jig_old, jig_new)

with open('core/engine.py', 'w') as f:
    f.write(code)

