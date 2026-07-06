import re

with open('core/foam_engine.py', 'r') as f: code = f.read()

new_method = """    def find_optimal_rotation_yz(self, f1, f2, ox, oy):
        if not f1 or not f2: return 0.0
        pts1 = self.parse_dxf(f1)
        pts2 = self.parse_dxf(f2)
        
        # Apply offsets BEFORE evaluating bounding box
        pts2[:, 0] += ox
        pts2[:, 1] += oy
        
        all_pts = np.vstack((pts1, pts2)).astype(float)
        cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
        cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
        all_pts -= np.array([cx, cy])

        min_height = float('inf')
        best_angle = 0.0
        # Check angles between -90 and 90 degrees with 0.5 degree precision
        for angle in np.arange(-90.0, 90.0, 0.5):
            rad = np.radians(angle)
            c, s = np.cos(rad), np.sin(rad)
            R = np.array([[c, -s], [s, c]])
            rotated = np.dot(all_pts, R.T)
            height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
            if height < min_height:
                min_height = height
                best_angle = angle

        return float(best_angle)
        
    def find_optimal_rotation"""

code = code.replace("    def find_optimal_rotation", new_method, 1)

with open('core/foam_engine.py', 'w') as f: f.write(code)
