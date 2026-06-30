#!/usr/bin/env python3

import os
import numpy as np

try:
    import ezdxf
except ImportError:
    ezdxf = None


# ==========================================
# 1. コアロジック層
# ==========================================
class FoamCutterEngine:
    def __init__(self):
        self.cached_file1 = ""
        self.cached_mtime1 = 0
        self.cached_pts1 = None
        
        self.cached_file2 = ""
        self.cached_mtime2 = 0
        self.cached_pts2 = None

    def parse_dxf(self, filepath):
        if ezdxf is None:
            raise ImportError("ezdxf is required. Run: pip install ezdxf")
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()
        
        paths = []
        for entity in msp.query('LWPOLYLINE LINE SPLINE ARC POLYLINE'):
            temp_points = []
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                with entity.points() as pts:
                    for p in pts:
                        temp_points.append([p[0], p[1]])
                if entity.closed and len(temp_points) > 0:
                    temp_points.append(temp_points[0])
                    
            elif entity.dxftype() == 'LINE':
                temp_points.append([entity.dxf.start.x, entity.dxf.start.y])
                temp_points.append([entity.dxf.end.x, entity.dxf.end.y])
                
            elif entity.dxftype() in ['SPLINE', 'ARC']:
                try:
                    for p in entity.flattening(distance=0.05):
                        temp_points.append([p[0], p[1]])
                    if entity.dxftype() == 'SPLINE' and entity.closed and len(temp_points) > 0:
                        if not np.allclose(temp_points[0], temp_points[-1], atol=1e-5):
                            temp_points.append(temp_points[0])
                except AttributeError:
                    pass
            if temp_points:
                paths.append(temp_points)
        return self._chain_paths(paths)

    def _chain_paths(self, paths_list):
        if not paths_list:
            return np.array([])
        paths = [np.array(p) for p in paths_list]
        chained = list(paths.pop(0))
        while paths:
            end_pt = chained[-1]
            found_idx, reverse = -1, False
            min_dist = float('inf')
            for i, p in enumerate(paths):
                dist_start = np.linalg.norm(p[0] - end_pt)
                dist_end = np.linalg.norm(p[-1] - end_pt)
                if dist_start < min_dist:
                    min_dist, found_idx, reverse = dist_start, i, False
                if dist_end < min_dist:
                    min_dist, found_idx, reverse = dist_end, i, True
                    
            best_path = paths.pop(found_idx)
            if reverse:
                chained.extend(best_path[::-1])
            else:
                chained.extend(best_path)
                
        cleaned = [chained[0]]
        for pt in chained[1:]:
            if np.linalg.norm(np.array(pt) - np.array(cleaned[-1])) > 1e-4:
                cleaned.append(pt)
        return np.array(cleaned)
        
    def _get_path_length(self, points):
        if len(points) < 2: return 0
        return np.sum(np.linalg.norm(np.diff(points, axis=0), axis=1))

    def _resample_points(self, points, target_count):
        if len(points) == target_count:
            return points
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
        distances = np.insert(distances, 0, 0)
        target_distances = np.linspace(0, distances[-1], target_count)
        
        # 鋭角の角を検出して保護する（面取り防止）
        corners = []
        for i in range(1, len(points)-1):
            v1 = points[i] - points[i-1]
            v2 = points[i+1] - points[i]
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 > 1e-5 and n2 > 1e-5:
                cos_th = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
                if np.arccos(cos_th) > 0.5: # 約28度以上の折れ曲がり
                    corners.append(distances[i])
        
        for c_dist in corners:
            idx = np.argmin(np.abs(target_distances - c_dist))
            if idx > 0 and c_dist <= target_distances[idx-1]: continue
            if idx < target_count - 1 and c_dist >= target_distances[idx+1]: continue
            target_distances[idx] = c_dist
            
        x_interp = np.interp(target_distances, distances, points[:, 0])
        y_interp = np.interp(target_distances, distances, points[:, 1])
        return np.column_stack((x_interp, y_interp))

    def _shift_path(self, pts, shift_pct):
        if len(pts) <= 1 or shift_pct == 0.0:
            return pts
        is_closed = np.linalg.norm(pts[0] - pts[-1]) < 1e-3
        idx = int((len(pts) - (1 if is_closed else 0)) * (shift_pct / 100.0))
        if idx == 0:
            return pts
        if is_closed:
            core = pts[:-1]
            shifted_core = np.roll(core, -idx, axis=0)
            return np.vstack((shifted_core, shifted_core[0]))
        else:
            return np.roll(pts, -idx, axis=0)

    def _apply_kerf_offset(self, points, kerf):
        if kerf == 0 or len(points) < 2:
            return points
        offset_points = np.zeros_like(points)
        offset = kerf / 2.0
        n_pts = len(points)
        
        is_closed = np.linalg.norm(points[0] - points[-1]) < 1e-3

        for i in range(n_pts):
            if is_closed:
                p0 = points[(i - 1) % (n_pts - 1)] if i == 0 else points[i - 1]
                p1 = points[i]
                p2 = points[(i + 1) % (n_pts - 1)] if i == n_pts - 1 else points[i + 1]
            else:
                p0 = points[i-1] if i > 0 else points[i]
                p1 = points[i]
                p2 = points[i+1] if i < n_pts-1 else points[i]

            t1 = p1 - p0
            t2 = p2 - p1
            
            n1, n2 = np.linalg.norm(t1), np.linalg.norm(t2)
            if n1 < 1e-10 and n2 < 1e-10:
                offset_points[i] = p1
                continue
                
            t1 = t1 / n1 if n1 > 1e-10 else t2 / n2
            t2 = t2 / n2 if n2 > 1e-10 else t1

            t = t1 + t2
            nt = np.linalg.norm(t)
            t = t / nt if nt > 1e-10 else t1

            n = np.array([-t[1], t[0]])
            offset_points[i] = p1 + n * offset
            
        if is_closed:
            offset_points[-1] = offset_points[0]
            
        return offset_points

    def compute_trajectory(self, f1, f2, kerf, wire_l, block_w, ox, oy, shift_pct, auto_center=True):
        if not f1 or not f2:
            raise ValueError("Files not specified")

        mtime1 = os.path.getmtime(f1) if os.path.exists(f1) else 0
        if f1 != self.cached_file1 or mtime1 != self.cached_mtime1 or self.cached_pts1 is None:
            self.cached_pts1 = self.parse_dxf(f1)
            self.cached_file1, self.cached_mtime1 = f1, mtime1

        mtime2 = os.path.getmtime(f2) if os.path.exists(f2) else 0
        if f2 != self.cached_file2 or mtime2 != self.cached_mtime2 or self.cached_pts2 is None:
            self.cached_pts2 = self.parse_dxf(f2)
            self.cached_file2, self.cached_mtime2 = f2, mtime2
            
        pts1 = np.copy(self.cached_pts1)
        pts2 = np.copy(self.cached_pts2)
        
        if auto_center:
            all_pts = np.vstack((pts1, pts2))
            cx = (np.min(all_pts[:, 0]) + np.max(all_pts[:, 0])) / 2.0
            cy = (np.min(all_pts[:, 1]) + np.max(all_pts[:, 1])) / 2.0
            pts1 -= np.array([cx, cy])
            pts2 -= np.array([cx, cy])

        len1 = self._get_path_length(pts1)
        len2 = self._get_path_length(pts2)
        density_pts = int(max(len1, len2) / 0.5)
        max_pts = max(len(pts1), len(pts2), density_pts)
        
        pts1 = self._shift_path(self._resample_points(pts1, max_pts), shift_pct)
        pts2 = self._shift_path(self._resample_points(pts2, max_pts), shift_pct)

        pts1 = self._apply_kerf_offset(pts1, kerf)
        pts2 = self._apply_kerf_offset(pts2, kerf)
        margin = (wire_l - block_w) / 2.0
        
        xy_traj, az_traj = [], []
        foam_xy, foam_az = [], [] 
        
        for i in range(max_pts):
            x_s, y_s = pts1[i][0] + ox, pts1[i][1] + oy
            u_s, v_s = pts2[i][0] + ox, pts2[i][1] + oy

            x_t = x_s - (u_s - x_s) * (margin / block_w)
            y_t = y_s - (v_s - y_s) * (margin / block_w)
            u_t = u_s + (u_s - x_s) * (margin / block_w)
            v_t = v_s + (v_s - y_s) * (margin / block_w)

            xy_traj.append([x_t, y_t])
            az_traj.append([u_t, v_t])
            foam_xy.append([x_s, y_s])
            foam_az.append([u_s, v_s])
            
        return np.array(xy_traj), np.array(az_traj), np.array(foam_xy), np.array(foam_az)

    def generate_gcode_string(self, traj_xy, traj_az, foam_xy, foam_az, ex, ey, axes, target_f, spindle_mode, s_value):
        ax_lh, ax_lv, ax_rh, ax_rv = axes
        cmd_m = "M4" if "M4" in spindle_mode else "M3"
        
        gcode = [
            "G21 ; Set units to millimeters", 
            "G90 ; Absolute positioning", 
            f"G0 {ax_lh}{ex:.3f} {ax_lv}{ey:.3f} {ax_rh}{ex:.3f} {ax_rv}{ey:.3f} ; Move to Entry Point",
            f"{cmd_m} S{s_value} ; Wire heat ON ({spindle_mode})"
        ]
        
        dlh, dlv = traj_xy[0][0] - ex, traj_xy[0][1] - ey
        drh, drv = traj_az[0][0] - ex, traj_az[0][1] - ey
        d_ctrl = np.sqrt(dlh**2 + dlv**2 + drh**2 + drv**2)
        d_foam = np.sqrt((foam_xy[0][0] - ex)**2 + (foam_xy[0][1] - ey)**2)
        
        if d_foam > 1e-5:
            f_cmd = min(target_f * (d_ctrl / d_foam), target_f * 5.0) 
        else:
            f_cmd = target_f
            
        gcode.append(f"G1 {ax_lh}{traj_xy[0][0]:.3f} {ax_lv}{traj_xy[0][1]:.3f} {ax_rh}{traj_az[0][0]:.3f} {ax_rv}{traj_az[0][1]:.3f} F{f_cmd:.1f} ; Lead-in")
        
        for i in range(1, len(traj_xy)):
            dlh = traj_xy[i][0] - traj_xy[i-1][0]
            dlv = traj_xy[i][1] - traj_xy[i-1][1]
            drh = traj_az[i][0] - traj_az[i-1][0]
            drv = traj_az[i][1] - traj_az[i-1][1]
            d_ctrl = np.sqrt(dlh**2 + dlv**2 + drh**2 + drv**2)
            
            d_foam_l = np.sqrt((foam_xy[i][0] - foam_xy[i-1][0])**2 + (foam_xy[i][1] - foam_xy[i-1][1])**2)
            d_foam_r = np.sqrt((foam_az[i][0] - foam_az[i-1][0])**2 + (foam_az[i][1] - foam_az[i-1][1])**2)
            d_foam_max = max(d_foam_l, d_foam_r)
            
            if d_foam_max > 1e-5:
                f_cmd = min(target_f * (d_ctrl / d_foam_max), target_f * 5.0)
            else:
                f_cmd = target_f
            
            val_lh, val_lv = traj_xy[i]
            val_rh, val_rv = traj_az[i]
            gcode.append(f"G1 {ax_lh}{val_lh:.3f} {ax_lv}{val_lv:.3f} {ax_rh}{val_rh:.3f} {ax_rv}{val_rv:.3f} F{f_cmd:.1f}")
            
        dlh, dlv = ex - traj_xy[-1][0], ey - traj_xy[-1][1]
        drh, drv = ex - traj_az[-1][0], ey - traj_az[-1][1]
        d_ctrl = np.sqrt(dlh**2 + dlv**2 + drh**2 + drv**2)
        d_foam = np.sqrt((ex - foam_xy[-1][0])**2 + (ey - foam_xy[-1][1])**2)
        
        if d_foam > 1e-5:
            f_cmd = min(target_f * (d_ctrl / d_foam), target_f * 5.0)
        else:
            f_cmd = target_f
        
        gcode.append(f"G1 {ax_lh}{ex:.3f} {ax_lv}{ey:.3f} {ax_rh}{ex:.3f} {ax_rv}{ey:.3f} F{f_cmd:.1f} ; Lead-out")
        gcode.append("M5 ; Wire heat OFF")
        gcode.append("M30 ; End of program")
        
        return "\n".join(gcode)