import numpy as np
import math
# Create an ellipse with X=200, Y=20
pts = []
for i in range(360):
    rad = math.radians(i)
    pts.append([100 * math.cos(rad), 10 * math.sin(rad)])
all_pts = np.array(pts)
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
print(f"Optimal angle for horizontal ellipse: {best_angle}, min_height: {min_height}")

all_pts_vertical = np.dot(all_pts, np.array([[0, -1], [1, 0]]).T)
min_height = float('inf')
best_angle = 0.0
for angle in np.arange(-90.0, 90.0, 0.5):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    R = np.array([[c, -s], [s, c]])
    rotated = np.dot(all_pts_vertical, R.T)
    height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
    if height < min_height:
        min_height = height
        best_angle = angle
print(f"Optimal angle for vertical ellipse: {best_angle}, min_height: {min_height}")
