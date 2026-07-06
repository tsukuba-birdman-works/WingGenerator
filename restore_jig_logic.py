import re

with open('recovered_jig.py', 'r') as f:
    jig_func_lines = f.readlines()

# Filter out EPHEMERAL_MESSAGE from end if any
clean_lines = []
for l in jig_func_lines:
    if "EPHEMERAL_MESSAGE" in l or "The following is an" in l or "<planning_mode>" in l:
        break
    clean_lines.append(l)

jig_func_str = "".join(clean_lines).strip()
# Modify signature to include return_full
jig_func_str = jig_func_str.replace("def generate_jig_at_y(self, p, y_local: float):", "def generate_jig_at_y(self, p, y_local: float, return_full=False):")

# Modify return block
return_block = """
        if getattr(frame, 'geom_type', '') == 'Polygon':
            jig_pts_out = list(frame.exterior.coords)
        elif getattr(frame, 'geom_type', '') == 'MultiPolygon':
            largest = max(frame.geoms, key=lambda a: a.area)
            jig_pts_out = list(largest.exterior.coords)
        else:
            jig_pts_out = []

        if return_full:
            return {
                'jig_pts': jig_pts_out,
                'wing_pts': np.column_stack((np.concatenate((u_x, l_x)), np.concatenate((u_y, l_y)))).tolist(),
                'c_m': tuple(c_m),
                'd_m': d_m,
                'c_f': tuple(c_f) if d_f > 0 else tuple(c_m),
                'd_f': d_f,
                'c_r': tuple(c_r) if d_r > 0 else tuple(c_m),
                'd_r': d_r
            }
        return jig_pts_out
"""

# Replace the old return block
old_return = """        if getattr(frame, 'geom_type', '') == 'Polygon':
            return list(frame.exterior.coords)
        elif getattr(frame, 'geom_type', '') == 'MultiPolygon':
            largest = max(frame.geoms, key=lambda a: a.area)
            return list(largest.exterior.coords)

        return []"""

if old_return in jig_func_str:
    jig_func_str = jig_func_str.replace(old_return, return_block.strip())
else:
    print("Warning: could not find old return block. I will append the return full logic.")

jig_func_str = "    " + jig_func_str.replace("\n", "\n    ")

with open('core/engine.py', 'r') as f:
    lines = f.readlines()

idx1 = -1
for i, l in enumerate(lines):
    if l.startswith("    def export_dxf(self, filepath, origin, rib_pts, c_m"):
        idx1 = i
        break

idx0 = -1
for i in range(idx1, -1, -1):
    if lines[i].startswith("    def generate_jig_at_y("):
        idx0 = i
        break

new_lines = lines[:idx0] + [jig_func_str + "\n\n"] + lines[idx1:]

with open('core/engine.py', 'w') as f:
    f.writelines(new_lines)
