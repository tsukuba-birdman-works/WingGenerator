import sys

filepath = '/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py'
with open(filepath, 'r') as f:
    content = f.read()

old_str = """            # 曲線群のコーナー数が一致するか確認
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
                corners = get_corners(c)
                
                pts_per_segment = max(2, n // len(corners))
                new_c = []
                for i in range(len(corners)):
                    start_idx = corners[i]
                    end_idx = corners[(i+1)%len(corners)]"""

new_str = """            # 曲線群のコーナー数が一致するか確認
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
                # Roll so that the primary corner is at index 0
                c = np.roll(c, -primary_idx, axis=0)
                # Recompute corners after roll to get their new indices
                corners, _ = get_corners(c, topo_type)
                
                pts_per_segment = max(2, n // len(corners))
                new_c = []
                for i in range(len(corners)):
                    start_idx = corners[i]
                    end_idx = corners[(i+1)%len(corners)]"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Not found!")
