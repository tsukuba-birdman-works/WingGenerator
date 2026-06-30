import numpy as np

def resample_closed_sharp(curve, n):
    if np.linalg.norm(curve[0] - curve[-1]) > 1e-5:
        curve = np.vstack([curve, curve[0]])
    dist = np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))
    dist = np.insert(dist, 0, 0)
    if dist[-1] == 0: return np.tile(curve[0], (n, 1))
    
    target = np.linspace(0, dist[-1], n)
    
    # 鋭角の角を検出
    corners = []
    for i in range(1, len(curve)-1):
        v1 = curve[i] - curve[i-1]
        v2 = curve[i+1] - curve[i]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            if np.arccos(cos_th) > 0.5: # 約28度以上の折れ曲がり
                corners.append(dist[i])
                
    # targetの対応するインデックスを角の距離にスナップ
    for c_dist in corners:
        idx = np.argmin(np.abs(target - c_dist))
        # 順序が逆転しないように保護
        if idx > 0 and c_dist <= target[idx-1]: continue
        if idx < n - 1 and c_dist >= target[idx+1]: continue
        target[idx] = c_dist

    return np.array([np.interp(target, dist, curve[:, i]) for i in range(curve.shape[1])]).T

curve = np.array([[0,0], [1,0], [1,1], [0,1], [0,0]])
res = resample_closed_sharp(curve, 10)
print(res)
