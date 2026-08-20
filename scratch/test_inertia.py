import numpy as np
def calc_polygon_inertia(pts):
    pts = np.array(pts)
    if not np.allclose(pts[0], pts[-1]):
        pts = np.vstack((pts, pts[0]))
    x = pts[:, 0]
    y = pts[:, 1]
    a = x[:-1] * y[1:] - x[1:] * y[:-1]
    A = 0.5 * np.sum(a)
    Cx = np.sum((x[:-1] + x[1:]) * a) / (6.0 * A)
    Cy = np.sum((y[:-1] + y[1:]) * a) / (6.0 * A)
    I_x = np.sum((y[:-1]**2 + y[:-1]*y[1:] + y[1:]**2) * a) / 12.0
    I_y = np.sum((x[:-1]**2 + x[:-1]*x[1:] + x[1:]**2) * a) / 12.0
    I_xx = abs(I_x - A * Cy**2)
    I_yy = abs(I_y - A * Cx**2)
    return abs(A), Cx, Cy, I_xx, I_yy

pts_ccw = [[0,0], [10,0], [10,5], [0,5]]
pts_cw  = [[0,0], [0,5], [10,5], [10,0]]

print("CCW:", calc_polygon_inertia(pts_ccw))
print("CW:", calc_polygon_inertia(pts_cw))
print("Expected I_xx (base*h^3/12):", 10 * 5**3 / 12)
print("Expected I_yy (h*base^3/12):", 5 * 10**3 / 12)
