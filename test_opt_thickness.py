import numpy as np

# Root: chord 100, thick 10 at (0,0)
t = np.linspace(0, 2*np.pi, 20)
x1 = 50 * np.cos(t) + 50
y1 = 5 * np.sin(t)
pts1 = np.column_stack((x1, y1))

# Tip: chord 50, thick 5, swept back by 50 in X and 20 in Y
x2 = 25 * np.cos(t) + 25 + 50
y2 = 2.5 * np.sin(t) + 20
pts2 = np.column_stack((x2, y2))

all_pts = np.vstack((pts1, pts2))

# Center the combined points
cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
all_pts -= np.array([cx, cy])

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
        
print("Best angle to minimize Y thickness:", best_angle)
print("Min height:", min_height)
print("Height at 0 angle:", np.max(all_pts[:, 1]) - np.min(all_pts[:, 1]))
