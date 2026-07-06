import numpy as np

# Create a mock airfoil: long in X (100), thin in Y (10)
t = np.linspace(0, 2*np.pi, 20)
x = 50 * np.cos(t)
y = 5 * np.sin(t)

all_pts = np.column_stack((x, y))

min_height = float('inf')
best_angle = 0.0
for angle in np.arange(-90.0, 90.0, 0.5):
    rad = np.radians(angle)
    c, s = np.cos(rad), np.sin(rad)
    R = np.array([[c, -s], [s, c]])
    rotated = np.dot(all_pts, R.T)
    height = np.max(rotated[:, 1]) - np.min(rotated[:, 1])
    width = np.max(rotated[:, 0]) - np.min(rotated[:, 0])
    
    if angle == 0.0: print("Angle 0: height=", height, "width=", width)
    if angle == 90.0 or angle == -90.0: print("Angle 90: height=", height, "width=", width)

    if height < min_height:
        min_height = height
        best_angle = angle
        
print("Best angle:", best_angle, "min height:", min_height)
