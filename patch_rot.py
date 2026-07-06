import re

with open('core/foam_engine.py', 'r') as f:
    content = f.read()

old_func = """    def find_optimal_rotation(self, f1, f2):
        if not f1 or not f2: return 0.0
        pts1 = self.parse_dxf(f1)
        pts2 = self.parse_dxf(f2)
        all_pts = np.vstack((pts1, pts2)).astype(float)
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

        return float(best_angle)"""

new_func = """    def find_optimal_rotation(self, f1, f2):
        if not f1 or not f2: return 0.0
        pts1 = self.parse_dxf(f1)
        pts2 = self.parse_dxf(f2)
        all_pts = np.vstack((pts1, pts2)).astype(float)
        cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
        cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
        all_pts -= np.array([cx, cy])

        min_height = float('inf')
        best_angle = 0.0
        # Check angles between -45 and 45 degrees with 0.5 degree precision
        import numpy as np
        for angle in np.arange(-45.0, 45.0, 0.5):
            rad = np.radians(angle)
            c, s = np.cos(rad), np.sin(rad)
            R = np.array([[c, -s], [s, c]])
            rotated = np.dot(all_pts, R.T)
            height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
            if height < min_height:
                min_height = height
                best_angle = angle

        return float(best_angle)"""

content = content.replace(old_func, new_func)

with open('core/foam_engine.py', 'w') as f:
    f.write(content)
print("foam_engine rotation updated")
