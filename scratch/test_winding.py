import numpy as np

def signed_area(pts):
    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - y * np.roll(x, -1))

# Let's make a simple dummy TE shape
u_x = np.linspace(100, 90, 5) # TE to LE
u_y = np.linspace(0, 5, 5) # Y positive

l_x = np.linspace(90, 100, 5) # LE to TE
l_y = np.linspace(-5, 0, 5) # Y negative

pts = np.column_stack((
    np.concatenate((u_x, l_x)),
    np.concatenate((u_y, l_y))
))

area = signed_area(pts)
print(f"Area: {area}")
print("If area > 0, it is CCW. If area < 0, it is CW.")
