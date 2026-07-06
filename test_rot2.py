import numpy as np
pts1 = np.array([[0,0], [100,0], [100,10], [0,10]])
pts2 = np.array([[0,0], [50,0], [50,5], [0,5]])
all_pts = np.vstack((pts1, pts2)).astype(float)
cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
all_pts -= np.array([cx, cy])

min_height = float('inf')
best_angle = 0.0
for angle in np.arange(-45.0, 45.0, 0.5):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    R = np.array([[c, -s], [s, c]])
    rotated = np.dot(all_pts, R.T)
    height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
    if height < min_height:
        min_height = height
        best_angle = angle
print(best_angle, min_height)
