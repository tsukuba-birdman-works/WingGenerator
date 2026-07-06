import re

# 1. Update core/foam_engine.py
with open('core/foam_engine.py', 'r') as f:
    engine_code = f.read()

# Remove the old find_optimal_rotation and find_optimal_rotation_yz
engine_code = re.sub(r'    def find_optimal_rotation_yz\(.*?(?=    def find_optimal_rotation\()', '', engine_code, flags=re.DOTALL)
engine_code = re.sub(r'    def find_optimal_rotation\(.*?(?=    def compute_trajectory\()', '', engine_code, flags=re.DOTALL)

# Insert the unified find_optimal_rotation
new_opt = """    def find_optimal_rotation(self, f1, f2, ox=0.0, oy=0.0):
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

"""
engine_code = engine_code.replace('    def compute_trajectory(', new_opt + '    def compute_trajectory(')

with open('core/foam_engine.py', 'w') as f:
    f.write(engine_code)


# 2. Update ui/foam_mode.py
with open('ui/foam_mode.py', 'r') as f:
    ui_code = f.read()

# Remove the YZ button
ui_code = re.sub(r'\s*tk\.Button\(rf, text="Min Thickness \(Y,Z\)", command=self\.optimize_rotation_yz\)\.pack\(side="left", padx=5\)', '', ui_code)

# Remove optimize_rotation_yz and replace optimize_rotation
ui_code = re.sub(r'    def optimize_rotation_yz\(.*?(?=    def optimize_rotation\()', '', ui_code, flags=re.DOTALL)
ui_code = re.sub(r'    def optimize_rotation\(.*?(?=    def browse_file\()', '', ui_code, flags=re.DOTALL)

new_ui_opt = """    def optimize_rotation(self):
        root_path = self.root_profile_path.get()
        tip_path = self.tip_profile_path.get()
        f1, f2 = (tip_path, root_path) if self.wing_type.get() == "Right" else (root_path, tip_path)
        try:
            ox = float(self.offset_x.get())
            oy = float(self.offset_y.get())
            opt_angle = self.engine.find_optimal_rotation(f1, f2, ox, oy)
            self.rotation_angle.set(round(opt_angle, 1))
            self.update_preview()
        except Exception as e:
            print(f"Optimization error: {e}")

"""
ui_code = ui_code.replace('    def browse_file(', new_ui_opt + '    def browse_file(')

with open('ui/foam_mode.py', 'w') as f:
    f.write(ui_code)
