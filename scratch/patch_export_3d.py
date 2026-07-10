import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# We need to change how te_part_coords is appended.
search = """            # Skins
            if len(res[13]) > 0: plank_curves.append(np.insert(self._to_rel(res[13], c_m), 1, y_ext, axis=1))
            if len(res[14]) > 0: te_curves.append(np.insert(self._to_rel(res[14], c_m), 1, y_ext, axis=1))
            if len(res[20]) > 0: film_curves.append(np.insert(self._to_rel(res[20], c_m), 1, y_ext, axis=1))"""

# Wait, we ran `git restore .` so `export_3d.py` is back to its original state.
# Let's check the original state first.
