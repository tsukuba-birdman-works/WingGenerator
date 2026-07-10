import sys
import os
sys.path.append(os.getcwd())
import numpy as np

# We can simulate the TE curves by making a wedge shape
curves = []
for scale in [1.0, 0.5]:
    # Rib 0: 3 corners (sharp TE)
    c = np.array([
        [-10, 2], # top front
        [0, 0],   # TE tip
        [-10, -2],# bottom front
        [-10, 0]  # extra point on front face
    ]) * scale
    
    # Let's add some points on the surfaces
    t_top = np.linspace(-10, 0, 10)*scale
    y_top = np.interp(t_top, [-10*scale, 0], [2*scale, 0])
    
    t_bot = np.linspace(0, -10, 10)*scale
    y_bot = np.interp(t_bot, [0, -10*scale], [0, -2*scale])
    
    c_full = []
    for x, y in zip(t_top, y_top): c_full.append([x, 0, y])
    for x, y in zip(t_bot[1:], y_bot[1:]): c_full.append([x, 0, y])
    c_full.append([-10*scale, 0, 0]) # front face mid point
    c_full.append([-10*scale, 0, 2*scale]) # close
    curves.append(np.array(c_full))

def get_corners(c):
    corners = []
    for i in range(len(c)):
        p_prev = c[i-1]
        p = c[i]
        p_next = c[(i+1)%len(c)]
        v1 = p - p_prev
        v2 = p_next - p
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            if np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)) > 0.5:
                corners.append(i)
    return corners

for i, c in enumerate(curves):
    c_core = c[:-1]
    print(f"Rib {i} corners: {get_corners(c_core)}")
