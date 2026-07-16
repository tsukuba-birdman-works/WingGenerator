import numpy as np

def simplify_curve(curve, tol=1e-3):
    # Remove collinear points
    res = [curve[0]]
    for i in range(1, len(curve)-1):
        v1 = curve[i] - res[-1]
        v2 = curve[i+1] - curve[i]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            if np.arccos(cos_th) > tol:
                res.append(curve[i])
    res.append(curve[-1])
    return np.array(res)

c = np.array([[0,0,0], [5,0,0], [10,0,0], [10,2,0], [0,2,0], [0,1,0], [0,0,0]])
print(simplify_curve(c))
