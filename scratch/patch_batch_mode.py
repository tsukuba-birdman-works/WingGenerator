import re

with open('ui/batch_mode.py', 'r') as f:
    content = f.read()

jig_append_code = """
            try:
                jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
                if jig_str:
                    jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                    for j_idx, jy in enumerate(jigs):
                        # Find closest rib index (or just assign a dummy idx)
                        # We use idx to get truss_angles_dict.
                        # It's better to find closest rib index to use its truss angle.
                        closest_idx = 0
                        min_dist = 99999
                        for r_idx, ry in enumerate(self.y_positions):
                            if abs(ry - jy) < min_dist:
                                min_dist = abs(ry - jy)
                                closest_idx = r_idx
                        items.append({'type': 'jig', 'idx': closest_idx, 'jig_idx': j_idx, 'y_local': jy, 'label': f"Jig {j_idx} (Y={jy + joint:.1f}mm)"})
            except Exception as e: print("Jig preview extraction error:", e)
"""

content = content.replace("self.preview_items = items", jig_append_code + "\n            self.preview_items = items")

with open('ui/batch_mode.py', 'w') as f:
    f.write(content)

