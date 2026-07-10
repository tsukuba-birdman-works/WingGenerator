import sys
import os

filepath = '/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py'
with open(filepath, 'r') as f:
    content = f.read()

# We need to replace get_corners and the topological resampler
old_get_corners = """            def get_corners(c, topo_type=None):
                if topo_type == 'TE_Skin':
                    idx_tip = np.argmax(c[:, 0])
                    min_x = np.min(c[:, 0])
                    front_indices = np.where(c[:, 0] < min_x + 2.0)[0]
                    if len(front_indices) == 0: front_indices = np.where(c[:, 0] < min_x + 5.0)[0]
                    if len(front_indices) > 0:
                        idx_top = front_indices[np.argmax(c[front_indices, 2])]
                        idx_bot = front_indices[np.argmin(c[front_indices, 2])]
                        corners = list(set([idx_tip, idx_top, idx_bot]))
                        corners.sort()
                        if len(corners) >= 3: return corners

                corners = []
                for i in range(len(c)):
                    p_prev = c[i-1]
                    p = c[i]
                    p_next = c[(i+1)%len(c)]
                    v1 = p - p_prev
                    v2 = p_next - p
                    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if n1 > 0.1 and n2 > 0.1:
                        if np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)) > 0.5:
                            corners.append(i)
                return corners"""

new_get_corners = """            def get_corners(c, topo_type=None):
                primary_idx = None
                if topo_type == 'TE_Skin':
                    idx_tip = np.argmax(c[:, 0])
                    min_x = np.min(c[:, 0])
                    front_indices = np.where(c[:, 0] < min_x + 2.0)[0]
                    if len(front_indices) == 0: front_indices = np.where(c[:, 0] < min_x + 5.0)[0]
                    if len(front_indices) > 0:
                        idx_top = front_indices[np.argmax(c[front_indices, 2])]
                        idx_bot = front_indices[np.argmin(c[front_indices, 2])]
                        corners = list(set([int(idx_tip), int(idx_top), int(idx_bot)]))
                        corners.sort()
                        if len(corners) >= 3: return corners, int(idx_tip)

                corners = []
                for i in range(len(c)):
                    p_prev = c[i-1]
                    p = c[i]
                    p_next = c[(i+1)%len(c)]
                    v1 = p - p_prev
                    v2 = p_next - p
                    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if n1 > 0.1 and n2 > 0.1:
                        if np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)) > 0.5:
                            corners.append(i)
                if len(corners) > 0:
                    # Pick the corner with the maximum X coordinate as the robust primary corner
                    primary_idx = corners[np.argmax([c[idx, 0] for idx in corners])]
                return corners, primary_idx"""

content = content.replace(old_get_corners, new_get_corners)

old_topo_check = """            # 曲線群のコーナー数が一致するか確認
            valid_curves_core = [c[:-1] if np.linalg.norm(c[0]-c[-1])<1e-5 else c for c in valid_curves]
            all_corners = [get_corners(c, topo_type) for c in valid_curves_core]
            topo_match = len(all_corners) > 0 and all(len(cn) == len(all_corners[0]) and len(cn) > 0 for cn in all_corners)
            print(f'topo_match: {topo_match}, all_corners lens: {[len(cn) for cn in all_corners]}', flush=True)

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
                corners = get_corners(c, topo_type)"""

new_topo_check = """            # 曲線群のコーナー数が一致するか確認
            valid_curves_core = [c[:-1] if np.linalg.norm(c[0]-c[-1])<1e-5 else c for c in valid_curves]
            all_corners_data = [get_corners(c, topo_type) for c in valid_curves_core]
            all_corners = [data[0] for data in all_corners_data]
            all_primary = [data[1] for data in all_corners_data]
            topo_match = len(all_corners) > 0 and all(len(cn) == len(all_corners[0]) and len(cn) > 0 for cn in all_corners)
            print(f'topo_match: {topo_match}, all_corners lens: {[len(cn) for cn in all_corners]}', flush=True)

            def resample_closed(curve, n, c_idx=0):
                if not topo_match or all_primary[c_idx] is None:
                    # Fallback to simple resampling
                    dist = np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))
                    dist = np.insert(dist, 0, 0)
                    if dist[-1] == 0: return np.tile(curve[0], (n, 1))
                    target = np.linspace(0, dist[-1], n)
                    return np.array([np.interp(target, dist, curve[:, i]) for i in range(3)]).T

                # Topological resampling
                c = valid_curves_core[c_idx]
                primary_idx = all_primary[c_idx]
                c = np.roll(c, -primary_idx, axis=0)
                corners, _ = get_corners(c, topo_type)"""

content = content.replace(old_topo_check, new_topo_check)

with open(filepath, 'w') as f:
    f.write(content)

print("Updated export_3d.py successfully!")
