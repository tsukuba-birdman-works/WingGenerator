import numpy as np
from shapely.geometry import Polygon

def resample_closed(curve, n):
    dist = np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))
    dist = np.insert(dist, 0, 0)
    if dist[-1] == 0: return np.tile(curve[0], (n, 1))
    target = np.linspace(0, dist[-1], n)
    corners = []
    for i in range(1, len(curve)-1):
        v1 = curve[i] - curve[i-1]
        v2 = curve[i+1] - curve[i]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            if np.arccos(cos_th) > 0.5:
                corners.append(dist[i])

    for c_dist in corners:
        idx = np.argmin(np.abs(target - c_dist))
        if idx == 0 or idx == n - 1: continue
        if c_dist <= target[idx-1]: continue
        if c_dist >= target[idx+1]: continue
        target[idx] = c_dist

    return np.array([np.interp(target, dist, curve[:, i]) for i in range(3)]).T

curve1 = np.array([[0,0,0], [30,0,0], [30,3,0], [0,0,0]])
c1_res = resample_closed(curve1, 50)
print(len(c1_res))
# Check if bottom corner and top corner are strictly inside
c_bottom = [30, 0, 0]
c_top = [30, 3, 0]
has_bottom = np.any(np.all(np.abs(c1_res - c_bottom) < 1e-5, axis=1))
has_top = np.any(np.all(np.abs(c1_res - c_top) < 1e-5, axis=1))
print(f"Has bottom: {has_bottom}, Has top: {has_top}")
