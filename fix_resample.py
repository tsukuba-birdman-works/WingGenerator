import sys
import os

with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'r') as f:
    content = f.read()

old_func = """            def resample_closed(curve, n):
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

                return np.array([np.interp(target, dist, curve[:, i]) for i in range(3)]).T"""

new_func = """            def get_corners(c):
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

            # 曲線群のコーナー数が一致するか確認
            valid_curves_core = [c[:-1] if np.linalg.norm(c[0]-c[-1])<1e-5 else c for c in valid_curves]
            all_corners = [get_corners(c) for c in valid_curves_core]
            topo_match = len(all_corners) > 0 and all(len(cn) == len(all_corners[0]) and len(cn) > 0 for cn in all_corners)

            def resample_closed(curve, n, c_idx=0):
                if not topo_match:
                    # Fallback to simple resampling
                    dist = np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))
                    dist = np.insert(dist, 0, 0)
                    if dist[-1] == 0: return np.tile(curve[0], (n, 1))
                    target = np.linspace(0, dist[-1], n)
                    return np.array([np.interp(target, dist, curve[:, i]) for i in range(3)]).T

                # Topological resampling
                c = valid_curves_core[c_idx]
                corners = all_corners[c_idx]
                c = np.roll(c, -corners[0], axis=0)
                corners = get_corners(c)
                
                pts_per_segment = max(2, n // len(corners))
                new_c = []
                for i in range(len(corners)):
                    start_idx = corners[i]
                    end_idx = corners[(i+1)%len(corners)]
                    segment = np.vstack([c[start_idx:], c[:end_idx+1]]) if end_idx < start_idx else c[start_idx:end_idx+1]
                    
                    dists = np.cumsum(np.linalg.norm(np.diff(segment, axis=0), axis=1))
                    dists = np.insert(dists, 0, 0)
                    if dists[-1] == 0:
                        resampled = np.tile(segment[0], (pts_per_segment, 1))
                    else:
                        target = np.linspace(0, dists[-1], pts_per_segment, endpoint=False)
                        resampled = np.array([np.interp(target, dists, segment[:, dim]) for dim in range(segment.shape[1])]).T
                    new_c.append(resampled)
                    
                return np.vstack(new_c)"""

if old_func in content:
    content = content.replace(old_func, new_func)
    
    # Also update the call to resample_closed to pass c_idx
    content = content.replace("c_res = resample_closed(c, max_len)", "c_res = resample_closed(c, max_len, i)")
    
    with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'w') as f:
        f.write(content)
    print("Replaced resample_closed successfully.")
else:
    print("Could not find old_func in export_3d.py")

