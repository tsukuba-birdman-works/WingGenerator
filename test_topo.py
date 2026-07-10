import numpy as np

def get_corners(c):
    corners = []
    for i in range(len(c)):
        p_prev = c[i-1]
        p = c[i]
        p_next = c[(i+1)%len(c)]
        v1 = p - p_prev
        v2 = p_next - p
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-5 and n2 > 1e-5:
            cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            if np.arccos(cos_th) > 0.5:
                corners.append(i)
    return corners

def topological_resample(curve, pts_per_segment=10):
    c = curve[:-1] if np.linalg.norm(curve[0]-curve[-1]) < 1e-5 else curve
    corners = get_corners(c)
    if len(corners) == 0:
        return curve # fallback
    
    # reorder so corners[0] is at index 0
    c = np.roll(c, -corners[0], axis=0)
    corners = get_corners(c) # recalculate indices
    
    new_c = []
    for i in range(len(corners)):
        start_idx = corners[i]
        end_idx = corners[(i+1)%len(corners)]
        if end_idx < start_idx:
            segment = np.vstack([c[start_idx:], c[:end_idx+1]])
        else:
            segment = c[start_idx:end_idx+1]
            
        # resample segment
        dists = np.cumsum(np.linalg.norm(np.diff(segment, axis=0), axis=1))
        dists = np.insert(dists, 0, 0)
        if dists[-1] == 0:
            resampled = np.tile(segment[0], (pts_per_segment, 1))
        else:
            target = np.linspace(0, dists[-1], pts_per_segment, endpoint=False)
            resampled = np.array([np.interp(target, dists, segment[:, dim]) for dim in range(segment.shape[1])]).T
        new_c.append(resampled)
        
    res = np.vstack(new_c)
    return np.vstack([res, res[0]])

# Test with a dummy triangle
c = np.array([[0,0], [10,0], [10,5]])
res = topological_resample(c, 5)
print(res)
