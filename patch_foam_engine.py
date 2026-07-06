import re

with open('core/foam_engine.py', 'r') as f:
    content = f.read()

# Add find_optimal_rotation method
new_method = """
    def find_optimal_rotation(self, f1, f2):
        if not f1 or not f2: return 0.0
        pts1 = self.parse_dxf(f1)
        pts2 = self.parse_dxf(f2)
        all_pts = np.vstack((pts1, pts2))
        cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
        cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
        all_pts -= np.array([cx, cy])

        min_area = float('inf')
        best_angle = 0.0
        for angle in range(0, 180):
            rad = np.radians(angle)
            c, s = np.cos(rad), np.sin(rad)
            R = np.array([[c, -s], [s, c]])
            rotated = np.dot(all_pts, R.T)
            width = np.max(rotated[:, 0]) - np.min(rotated[:, 0])
            height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
            area = width * height
            if area < min_area:
                min_area = area
                best_angle = angle

        return float(best_angle)

"""

# Insert before compute_trajectory
content = content.replace("    def compute_trajectory(", new_method + "    def compute_trajectory(")

# Update compute_trajectory signature
content = content.replace(
    "compute_trajectory(self, f1, f2, kerf, wire_l, block_w, ox, oy, shift_pct, auto_center=True, reverse_path=False, smooth_curves=False):",
    "compute_trajectory(self, f1, f2, kerf, wire_l, block_w, ox, oy, shift_pct, auto_center=True, reverse_path=False, smooth_curves=False, rotation_angle=0.0):"
)

# Apply rotation in compute_trajectory
rot_logic = """
        if rotation_angle != 0.0:
            rad = np.radians(rotation_angle)
            c, s = np.cos(rad), np.sin(rad)
            R = np.array([[c, -s], [s, c]])
            pts1 = np.dot(pts1, R.T)
            pts2 = np.dot(pts2, R.T)

        pts1[:, 0] += ox; pts1[:, 1] += oy
"""
content = content.replace(
    "pts1[:, 0] += ox; pts1[:, 1] += oy",
    rot_logic
)

with open('core/foam_engine.py', 'w') as f:
    f.write(content)
print("foam_engine patched")
