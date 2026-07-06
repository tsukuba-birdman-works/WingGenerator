import numpy as np

# Root: chord 100, thick 10 at (0,0)
t = np.linspace(0, 2*np.pi, 20)
x1 = 50 * np.cos(t) + 50
y1 = 5 * np.sin(t)
pts1 = np.column_stack((x1, y1))

# Tip: chord 50, thick 5. But offset by sweep in FoamCutterGUI:
# Wait! In FoamCutterGUI, find_optimal_rotation does NOT know about offset!
# So pts2 is just at (0,0) in DXF!
x2 = 25 * np.cos(t) + 25
y2 = 2.5 * np.sin(t)
pts2 = np.column_stack((x2, y2))

all_pts = np.vstack((pts1, pts2))

min_height = float('inf')
best_angle = 0.0
for angle in np.arange(-90.0, 90.0, 0.5):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    R = np.array([[c, -s], [s, c]])
    rotated = np.dot(all_pts, R.T)
    height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
    
    if height < min_height:
        min_height = height
        best_angle = angle
        
print("Best angle:", best_angle)
