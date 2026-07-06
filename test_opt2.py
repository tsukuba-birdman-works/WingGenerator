import numpy as np

pts = np.array([
    [0, 0], [200, 0], [200, 20], [0, 20], [0, 0]
])
cx = (np.min(pts[:, 0]) + np.max(pts[:, 0])) / 2.0
cy = (np.min(pts[:, 1]) + np.max(pts[:, 1])) / 2.0
pts -= np.array([cx, cy])

min_height = float('inf')
best_angle = 0
for angle in np.arange(-90.0, 90.0, 0.5):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    R = np.array([[c, -s], [s, c]])
    rotated = np.dot(pts, R.T)
    height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
    width = np.max(rotated[:, 0]) - np.min(rotated[:, 0])
    if height < min_height:
        min_height = height
        best_angle = angle

print(f"best angle: {best_angle}, min_height: {min_height}")
