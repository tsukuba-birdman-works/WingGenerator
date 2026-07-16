import numpy as np

def detect_corners(c):
    dist = np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))
    dist = np.insert(dist, 0, 0)
    corners = [0]
    for i in range(1, len(c)-1):
        v1 = c[i] - c[i-1]
        v2 = c[i+1] - c[i]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            if np.arccos(cos_th) > 0.5:
                corners.append(i)
    return corners, dist

# Test with dummy data
r1 = np.array([[0, 0, 0], [30, 0, 0], [30, 0, 3], [0, 0, 3], [0,0,0]])
c, d = detect_corners(r1)
print(c)
