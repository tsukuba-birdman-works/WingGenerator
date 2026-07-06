import re

with open('core/engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace resample_airfoil
old_func = """    def resample_airfoil(self, points, target_count=300):
        if len(points) == 0: return points
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
        distances = np.insert(distances, 0, 0)
        target_distances = np.linspace(0, distances[-1], target_count)
        x_interp = np.interp(target_distances, distances, points[:, 0])
        y_interp = np.interp(target_distances, distances, points[:, 1])
        return np.column_stack((x_interp, y_interp))"""

new_func = """    def resample_airfoil(self, points, target_count=300, smooth=False):
        if len(points) < 2: return points
        diffs = np.diff(points, axis=0)
        distances = np.cumsum(np.linalg.norm(diffs, axis=1))
        distances = np.insert(distances, 0, 0)
        if distances[-1] == 0:
            return np.full((target_count, 2), points[0])

        target_distances = np.linspace(0, distances[-1], target_count)

        corner_indices = [0]
        for i in range(1, len(points)-1):
            v1 = points[i] - points[i-1]
            v2 = points[i+1] - points[i]
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 > 1e-5 and n2 > 1e-5:
                cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
                if np.arccos(cos_th) > 0.5:
                    corner_indices.append(i)
        corner_indices.append(len(points)-1)

        for idx in corner_indices:
            c_dist = distances[idx]
            t_idx = np.argmin(np.abs(target_distances - c_dist))
            if t_idx > 0 and c_dist <= target_distances[t_idx-1]: continue
            if t_idx < target_count - 1 and c_dist >= target_distances[t_idx+1]: continue
            target_distances[t_idx] = c_dist

        if not smooth:
            x_interp = np.interp(target_distances, distances, points[:, 0])
            y_interp = np.interp(target_distances, distances, points[:, 1])
            return np.column_stack((x_interp, y_interp))
        else:
            try:
                from scipy.interpolate import make_interp_spline
            except ImportError:
                x_interp = np.interp(target_distances, distances, points[:, 0])
                y_interp = np.interp(target_distances, distances, points[:, 1])
                return np.column_stack((x_interp, y_interp))

            x_interp = np.zeros(target_count)
            y_interp = np.zeros(target_count)

            for k in range(len(corner_indices)-1):
                start_i = corner_indices[k]
                end_i = corner_indices[k+1]
                d_start = distances[start_i]
                d_end = distances[end_i]

                t_mask = (target_distances >= d_start) & (target_distances <= d_end)
                t_segment = target_distances[t_mask]
                if len(t_segment) == 0: continue

                seg_points = points[start_i:end_i+1]
                seg_dists = distances[start_i:end_i+1]

                unique_idx = np.unique(seg_dists, return_index=True)[1]
                seg_dists = seg_dists[unique_idx]
                seg_points = seg_points[unique_idx]

                if len(seg_points) < 2:
                    x_interp[t_mask] = seg_points[0, 0]
                    y_interp[t_mask] = seg_points[0, 1]
                elif len(seg_points) < 4:
                    x_interp[t_mask] = np.interp(t_segment, seg_dists, seg_points[:, 0])
                    y_interp[t_mask] = np.interp(t_segment, seg_dists, seg_points[:, 1])
                else:
                    try:
                        spline_x = make_interp_spline(seg_dists, seg_points[:, 0], k=3)
                        spline_y = make_interp_spline(seg_dists, seg_points[:, 1], k=3)
                        x_interp[t_mask] = spline_x(t_segment)
                        y_interp[t_mask] = spline_y(t_segment)
                    except Exception:
                        x_interp[t_mask] = np.interp(t_segment, seg_dists, seg_points[:, 0])
                        y_interp[t_mask] = np.interp(t_segment, seg_dists, seg_points[:, 1])

            return np.column_stack((x_interp, y_interp))"""

content = content.replace(old_func, new_func)

# Also update the calls to resample_airfoil
smooth_var = "smooth_curves = p.get('smooth_curves', False)\n            "
call1 = "blended = self.resample_airfoil(pts1, n_pts) * (1.0 - t) + self.resample_airfoil(pts2, n_pts) * t"
call1_new = smooth_var + "blended = self.resample_airfoil(pts1, n_pts, smooth=smooth_curves) * (1.0 - t) + self.resample_airfoil(pts2, n_pts, smooth=smooth_curves) * t"

call2 = "blended = self.resample_airfoil(pts1, n_pts) * (1.0 - blend_ratio) + self.resample_airfoil(pts2, n_pts) * blend_ratio"
call2_new = smooth_var.replace('p.get', 'params.get') + "blended = self.resample_airfoil(pts1, n_pts, smooth=smooth_curves) * (1.0 - blend_ratio) + self.resample_airfoil(pts2, n_pts, smooth=smooth_curves) * blend_ratio"

content = content.replace(call1, call1_new)
content = content.replace(call2, call2_new)

with open('core/engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated engine.py")
