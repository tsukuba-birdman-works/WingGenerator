import os
import traceback
import numpy as np
import warnings

# GEOS(Shapely)内部の微小なトポロジー計算エラーの警告を非表示にする
warnings.filterwarnings("ignore", category=RuntimeWarning)

try:
    import ezdxf
except ImportError:
    ezdxf = None

try:
    from shapely.geometry import Polygon, Point, LineString
    from shapely.ops import unary_union, split
    from shapely.affinity import scale
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False


from dataclasses import dataclass, field
from typing import NamedTuple, List, Dict, Any, Tuple

@dataclass
class RibParameters:
    file1: str
    file2: str
    blend_ratio: float
    chord: float
    spar_pct: float
    washout_deg: float
    spar_hole_dia: float
    spar_hole_dv: float
    rear_dx: float
    rear_dy: float
    rear_dia: float
    front_dx: float
    front_dy: float
    front_dia: float
    truss_angle: float
    truss_front_n: int
    truss_rear_n: int

    beam_width: float
    margin_spar: float
    margin_bolt: float
    margin_outer: float
    truss_fillet: float
    min_hole_dia: float
    xb_t_list: List[float]
    x_dia: float
    plank_start: float
    plank_end: float
    plank_part_start: float
    plank_part_end: float
    plank_thick: float
    stringers_data: List[Dict[str, Any]]
    te_cut: float
    apply_safe_margin: bool
    le_interp_active: bool
    le_interp_range: float
    le_interp_divisions: int
    te_cap_uf_act: bool
    te_cap_uf_w: float
    te_cap_ur_act: bool
    te_cap_ur_w: float
    te_cap_lf_act: bool
    te_cap_lf_w: float
    te_cap_lr_act: bool
    te_cap_lr_w: float
    te_cap_thick: float
    rc1_act: bool
    rc1_start: float
    rc1_end: float
    rc1_thick: float
    rc2_act: bool
    rc2_start: float
    rc2_end: float
    rc2_thick: float
    bolt1_dx: float = 0.0
    truss_scale_front_list: List[float] = field(default_factory=list)
    truss_scale_rear_list: List[float] = field(default_factory=list)
    bolt1_dy: float = 0.0
    bolt1_dia: float = 0.0
    bolt2_dx: float = 0.0
    bolt2_dy: float = 0.0
    bolt2_dia: float = 0.0
    diag_params_list: List[Dict[str, Any]] = field(default_factory=list)
    fast_mode: bool = False
    tabs_active: bool = True
    truss_tab_width: float = 4.0

class RibGenerationResult(NamedTuple):
    final_rib_mod: Any
    c_m: Any
    hole_m: Any
    c_r: Any
    hole_r: Any
    c_f: Any
    hole_f: Any
    final_truss_holes: List[Any]
    xb_r_active: List[Any]
    active_xb_centers: List[Any]
    xb_r_skipped: List[Any]
    skipped_xb_centers: List[Any]
    warnings_list: List[str]
    plank_poly_rot: Any
    te_part_coords: Any
    c_b1: Any
    hole_b1: Any
    c_b2: Any
    hole_b2: Any
    diag_poly_pts_list: List[Any]
    final_rib_orig: Any
    stringer_pts_list: List[Any]
    te_cap_pts_list: List[Any]
    rc_cap_pts_list: List[Any]
    tab_centers: Any = None


# ==========================================
# 1. コアロジック層 (Rib Engine)
# ==========================================
class RibGeneratorEngine:
    def __init__(self):
        self.dxf_cache = {}

    def load_dat(self, filepath):
        pts = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        x, y = float(parts[0]), float(parts[1])
                        pts.append([x, y])
                    except ValueError:
                        continue
        return np.array(pts)

    def load_dxf_profile(self, filepath):
        if ezdxf is None or not filepath or not os.path.exists(filepath):
            return None
        if filepath in self.dxf_cache:
            return self.dxf_cache[filepath]
            
        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            pts = []
            lines = []
            
            for entity in msp:
                if entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                    pts = [p[:2] for p in entity.get_points()]
                    break
                elif entity.dxftype() == 'LINE':
                    lines.append((entity.dxf.start[:2], entity.dxf.end[:2]))
            
            if not pts and lines:
                pts.append(list(lines[0][0]))
                pts.append(list(lines[0][1]))
                lines.pop(0)
                while lines:
                    last_pt = pts[-1]
                    found = False
                    for i, l in enumerate(lines):
                        if np.linalg.norm(np.array(l[0]) - np.array(last_pt)) < 1e-4:
                            pts.append(list(l[1]))
                            lines.pop(i)
                            found = True
                            break
                        elif np.linalg.norm(np.array(l[1]) - np.array(last_pt)) < 1e-4:
                            pts.append(list(l[0]))
                            lines.pop(i)
                            found = True
                            break
                    if not found:
                        break

            if not pts: return None
            pts = np.array(pts)
            max_x = np.max(pts[:, 0])
            min_y = np.min(pts[:, 1])
            pts[:, 0] -= max_x
            pts[:, 1] -= min_y
            
            self.dxf_cache[filepath] = pts
            return pts
        except:
            return None

    def resample_airfoil(self, points, target_count=300):
        if len(points) == 0: return points
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
        distances = np.insert(distances, 0, 0)
        target_distances = np.linspace(0, distances[-1], target_count)
        x_interp = np.interp(target_distances, distances, points[:, 0])
        y_interp = np.interp(target_distances, distances, points[:, 1])
        return np.column_stack((x_interp, y_interp))

    def get_loop_curve(self, u_x, u_y, l_x, l_y, chord):
        l_x_rev = l_x[::-1]
        l_y_rev = l_y[::-1]
        
        x_all = np.concatenate((l_x_rev[:-1], u_x))
        y_all = np.concatenate((l_y_rev[:-1], u_y))
        
        s_all = np.zeros_like(x_all)
        n_lower = len(l_x_rev) - 1
        s_all[:n_lower] = -(x_all[:n_lower] / chord) * 100.0
        s_all[n_lower:] = (x_all[n_lower:] / chord) * 100.0
        
        # s_all が単調増加になるように強制する (微小なブレ対策)
        for i in range(1, len(s_all)):
            if s_all[i] <= s_all[i-1]:
                s_all[i] = s_all[i-1] + 1e-6
                
        dx = np.gradient(x_all)
        dy = np.gradient(y_all)
        norm = np.sqrt(dx**2 + dy**2)
        norm[norm == 0] = 1.0
        nx = dy / norm
        ny = -dx / norm
        
        return x_all, y_all, s_all, nx, ny, n_lower

    def get_slice_curve(self, x_all, y_all, s_all, nx, ny, min_p, max_p):
        mask = (s_all > min_p) & (s_all < max_p)
        if not np.any(mask) and not (s_all[0] <= min_p <= s_all[-1] or s_all[0] <= max_p <= s_all[-1]):
            return np.array([]), np.array([]), np.array([]), np.array([])
            
        s_slice = [min_p] + list(s_all[mask]) + [max_p]
        s_slice = sorted(list(set(s_slice)))
        
        x_slice = np.interp(s_slice, s_all, x_all)
        y_slice = np.interp(s_slice, s_all, y_all)
        nx_slice = np.interp(s_slice, s_all, nx)
        ny_slice = np.interp(s_slice, s_all, ny)
        
        # normalize nx, ny
        norm = np.sqrt(nx_slice**2 + ny_slice**2)
        norm[norm == 0] = 1.0
        nx_slice /= norm
        ny_slice /= norm
        
        return x_slice, y_slice, nx_slice, ny_slice

    def get_smoothed_guideline(self, x_orig, y_orig, chord, plank_start, plank_end, plank_thick, is_upper):
        s_orig = (x_orig / chord) * 100.0
        if not is_upper:
            s_orig = -s_orig
            
        min_p = min(plank_start, plank_end)
        max_p = max(plank_start, plank_end)
        
        ramp_pct = 5.0 
        t_smooth = np.zeros_like(x_orig)
        
        if plank_thick != 0:
            for i, s in enumerate(s_orig):
                if min_p <= s <= max_p:
                    t_smooth[i] = plank_thick
                elif s < min_p and s >= min_p - ramp_pct:
                    t_smooth[i] = plank_thick * (s - (min_p - ramp_pct)) / ramp_pct
                elif s > max_p and s <= max_p + ramp_pct:
                    t_smooth[i] = plank_thick * ((max_p + ramp_pct) - s) / ramp_pct
                else:
                    t_smooth[i] = 0.0
                
        dx = np.gradient(x_orig)
        dy = np.gradient(y_orig)
        norm = np.sqrt(dx**2 + dy**2)
        norm[norm == 0] = 1.0
        tx = dx / norm
        ty = dy / norm
        nx, ny = (ty, -tx) if is_upper else (-ty, tx)
        
        x_guide = x_orig + nx * t_smooth
        y_guide = y_orig + ny * t_smooth
        
        for i in range(1, len(x_guide)):
            if x_guide[i] <= x_guide[i-1]: 
                x_guide[i] = x_guide[i-1] + 1e-5
                    
        return x_guide, y_guide

    def apply_plank_offset(self, u_x, u_y, l_x, l_y, start_pct, end_pct, part_start_pct, part_end_pct, thickness, chord):
        if thickness == 0 or start_pct == end_pct:
            return u_x, u_y, l_x, l_y, []

        x_all, y_all, s_all, nx, ny, _ = self.get_loop_curve(u_x, u_y, l_x, l_y, chord)
        
        min_p = min(start_pct, end_pct)
        max_p = max(start_pct, end_pct)
        
        s_new = []
        for i in range(len(s_all) - 1):
            s1, s2 = s_all[i], s_all[i+1]
            s_new.append(s1)
            if s1 < min_p < s2: s_new.append(min_p)
            if s1 < max_p < s2: s_new.append(max_p)
        s_new.append(s_all[-1])
        s_new = np.array(s_new)
        
        x_new = np.interp(s_new, s_all, x_all)
        y_new = np.interp(s_new, s_all, y_all)
        nx_new = np.interp(s_new, s_all, nx)
        ny_new = np.interp(s_new, s_all, ny)
        
        norm = np.sqrt(nx_new**2 + ny_new**2)
        norm[norm == 0] = 1.0
        nx_new /= norm
        ny_new /= norm
        
        mask = (s_new >= min_p) & (s_new <= max_p)
        
        res_x, res_y = [], []
        for i in range(len(s_new)):
            if mask[i] and i > 0 and not mask[i-1]:
                res_x.append(x_new[i]); res_y.append(y_new[i])
            if mask[i]:
                res_x.append(x_new[i] + nx_new[i] * thickness)
                res_y.append(y_new[i] + ny_new[i] * thickness)
            else:
                res_x.append(x_new[i])
                res_y.append(y_new[i])
            if mask[i] and i < len(s_new)-1 and not mask[i+1]:
                res_x.append(x_new[i]); res_y.append(y_new[i])
                
        res_x, res_y = np.array(res_x), np.array(res_y)
        le_idx = np.argmin(res_x)
        l_x_mod, l_y_mod = res_x[:le_idx+1][::-1], res_y[:le_idx+1][::-1]
        u_x_mod, u_y_mod = res_x[le_idx:], res_y[le_idx:]
        
        plank_poly_pts = []
        part_min_p = min(part_start_pct, part_end_pct)
        part_max_p = max(part_start_pct, part_end_pct)
        
        p_x_out, p_y_out, p_nx, p_ny = self.get_slice_curve(x_all, y_all, s_all, nx, ny, part_min_p, part_max_p)
        if len(p_x_out) > 0:
            p_x_in = p_x_out + p_nx * thickness
            p_y_in = p_y_out + p_ny * thickness
            p_x = np.concatenate([p_x_out, p_x_in[::-1], [p_x_out[0]]])
            p_y = np.concatenate([p_y_out, p_y_in[::-1], [p_y_out[0]]])
            plank_poly_pts = np.column_stack((p_x, p_y))
        
        return u_x_mod, u_y_mod, l_x_mod, l_y_mod, plank_poly_pts

    def apply_stringer_grooves(self, rib_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig, chord, spar_x, spar_y, R_mat, stringers_data, plank_start, plank_end, plank_thick):
        if not stringers_data or not SHAPELY_AVAILABLE:
            return rib_poly, []
            
        x_all, y_all, s_all, nx, ny, n_lower = self.get_loop_curve(u_x_orig, u_y_orig, l_x_orig, l_y_orig, chord)
        groove_polys = []
        groove_pts_list = []
        
        min_p = min(plank_start, plank_end)
        max_p = max(plank_start, plank_end)
        
        for st in stringers_data:
            p = st['pos']
            width = st['w']
            depth = st['d']
            dxf_pts = st.get('dxf_pts')
                
            P_orig_x = np.interp(p, s_all, x_all)
            P_orig_y = np.interp(p, s_all, y_all)
            nx_interp = np.interp(p, s_all, nx)
            ny_interp = np.interp(p, s_all, ny)
            
            norm = np.sqrt(nx_interp**2 + ny_interp**2)
            if norm == 0: norm = 1.0
            nx_interp /= norm
            ny_interp /= norm
            
            P_orig = np.array([P_orig_x, P_orig_y])
            vec_n = np.array([nx_interp, ny_interp])
            vec_t_loop = np.array([-ny_interp, nx_interp])
            
            vec_t_LE = vec_t_loop if p < 0 else -vec_t_loop
            s_eval = p - 0.1 if p > 0 else p + 0.1
            if p == 0: s_eval = 0
            is_offset = (min_p <= s_eval <= max_p)
            local_t = plank_thick if is_offset else 0.0
            
            eps_out = 5.0
            eps_TE = 1e-3
            
            if dxf_pts is not None and len(dxf_pts) >= 3:
                poly_pts = []
                stringer_poly_pts = []
                P_surf = P_orig + vec_n * local_t
                for pt in dxf_pts:
                    dx, dy = pt[0], pt[1]
                    mapped_st = P_surf - dx * vec_t_LE + dy * vec_n
                    stringer_poly_pts.append(mapped_st)
                    
                    if dy <= 0.001: dy = -eps_out
                    if dx >= -0.001: dx = eps_TE
                    mapped = P_surf - dx * vec_t_LE + dy * vec_n
                    poly_pts.append(mapped)
            else:
                P_surf = P_orig + vec_n * local_t
                P_TE_out = P_surf - vec_n * eps_out     - vec_t_LE * eps_TE
                P_TE_in  = P_surf + vec_n * depth       - vec_t_LE * eps_TE
                P_LE_in  = P_surf + vec_n * depth       + vec_t_LE * width
                P_LE_out = P_surf - vec_n * eps_out     + vec_t_LE * width
                poly_pts = [P_TE_out, P_TE_in, P_LE_in, P_LE_out]
                
                S_TE_out = P_surf
                S_TE_in  = P_surf + vec_n * depth
                S_LE_in  = P_surf + vec_n * depth       + vec_t_LE * width
                S_LE_out = P_surf                       + vec_t_LE * width
                stringer_poly_pts = [S_TE_out, S_TE_in, S_LE_in, S_LE_out]
                
            rot_pts = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in poly_pts]
            rot_st_pts = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in stringer_poly_pts]
            
            try:
                gp = Polygon(rot_pts).buffer(0)
                if gp.is_valid and not gp.is_empty:
                    groove_polys.append(gp)
                    groove_pts_list.append(np.array(rot_st_pts))
            except Exception: pass
                
        if groove_polys:
            try:
                safe_union = unary_union(groove_polys).buffer(0)
                rib_poly = rib_poly.buffer(0).difference(safe_union).buffer(0)
                if getattr(rib_poly, 'geom_type', '') == 'MultiPolygon':
                    rib_poly = max(rib_poly.geoms, key=lambda a: a.area)
            except Exception: pass
                
        return rib_poly, groove_pts_list

    def apply_rib_caps(self, rib_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig, chord, spar_x, spar_y, R_mat,
                       rc1_act, rc1_start, rc1_end, rc1_thick,
                       rc2_act, rc2_start, rc2_end, rc2_thick):
        if not SHAPELY_AVAILABLE:
            return rib_poly, ([], [])
            
        x_all, y_all, s_all, nx, ny, n_lower = self.get_loop_curve(u_x_orig, u_y_orig, l_x_orig, l_y_orig, chord)
        
        cap_pts1, cap_pts2 = [], []
        
        for idx, (act, start_pct, end_pct, cap_thick) in enumerate([(rc1_act, rc1_start, rc1_end, rc1_thick), (rc2_act, rc2_start, rc2_end, rc2_thick)]):
            if not act or start_pct == end_pct: continue
            
            min_p = min(start_pct, end_pct)
            max_p = max(start_pct, end_pct)
            
            x_surf, y_surf, nx_surf, ny_surf = self.get_slice_curve(x_all, y_all, s_all, nx, ny, min_p, max_p)
            if len(x_surf) == 0: continue
            
            in_bound, cap_surf = [], []
            
            t = max(cap_thick, 0.1) if cap_thick > 0 else 0.1
            for i in range(len(x_surf)):
                p = np.array([x_surf[i], y_surf[i]])
                n = np.array([nx_surf[i], ny_surf[i]])
                
                # nx, ny は内向き法線なので、外側に浮かせるにはマイナスをかける
                in_bound.append(p - n * 0.1)
                cap_surf.append(p - n * (0.1 + t))
                
            cap_geom = cap_surf + in_bound[::-1]
            rot_cap = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in cap_geom]
            
            try:
                cap_poly = Polygon(rot_cap).buffer(0)
                if not cap_poly.is_empty:
                    if getattr(cap_poly, 'geom_type', '') == 'MultiPolygon': 
                        for cp in cap_poly.geoms:
                            if idx == 0: cap_pts1.append(np.array(cp.exterior.coords))
                            else: cap_pts2.append(np.array(cp.exterior.coords))
                    else:
                        if idx == 0: cap_pts1.append(np.array(cap_poly.exterior.coords))
                        else: cap_pts2.append(np.array(cap_poly.exterior.coords))
            except Exception: pass
            
        return rib_poly, (cap_pts1, cap_pts2)

    def apply_te_caps(self, rib_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig, te_cut, cap_thick, spar_x, spar_y, R_mat,
                      uf_act, uf_w, ur_act, ur_w, lf_act, lf_w, lr_act, lr_w):
        if not SHAPELY_AVAILABLE or te_cut <= 0:
            return rib_poly, []
            
        u_pts_rev = np.column_stack((u_x_orig[::-1], u_y_orig[::-1]))
        dist_u = np.zeros(len(u_pts_rev))
        dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))
        
        l_pts_rev = np.column_stack((l_x_orig[::-1], l_y_orig[::-1]))
        dist_l = np.zeros(len(l_pts_rev))
        dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))

        groove_polys = []
        cap_pts_list = []
        
        te_start = te_cut + 10.0 # 後縁材の前縁側位置（+10mmオーバーラップ）
        t = max(cap_thick, 0.1) if cap_thick > 0 else 0.1
        
        def build_cap(pts_rev, dist_arr, is_upper):
            f_act = uf_act if is_upper else lf_act
            f_w = uf_w if is_upper else lf_w
            r_act = ur_act if is_upper else lr_act
            r_w = ur_w if is_upper else lr_w
            
            zones = []
            if f_act and f_w > 0: zones.append((te_cut + f_w, te_cut, True))
            if r_act and r_w > 0: zones.append((r_w, 0.0, False))
            
            for start_d, end_d, is_front in zones:
                if start_d <= 0 or start_d <= end_d: continue
                
                p_start = np.array([np.interp(start_d, dist_arr, pts_rev[:, 0]), np.interp(start_d, dist_arr, pts_rev[:, 1])])
                p_end = np.array([np.interp(end_d, dist_arr, pts_rev[:, 0]), np.interp(end_d, dist_arr, pts_rev[:, 1])])
                
                mask = (dist_arr < start_d) & (dist_arr > end_d)
                inner_pts = pts_rev[mask]
                
                surf_pts = [p_start]
                if len(inner_pts) > 0: surf_pts.extend(inner_pts)
                surf_pts.append(p_end)
                surf_pts = np.array(surf_pts)
                
                n_pts = len(surf_pts)
                in_bound, out_bound, cap_surf = [], [], []
                eps_out = 5.0
                
                for i in range(n_pts):
                    p = surf_pts[i]
                    if i < n_pts - 1: v = surf_pts[i+1] - p
                    else: v = p - surf_pts[i-1]
                    
                    n = np.array([-v[1], v[0]])
                    n = n / np.linalg.norm(n) if np.linalg.norm(n) > 0 else np.array([0, 1])
                    
                    if is_upper: n = -n if n[1] < 0 else n
                    else: n = -n if n[1] > 0 else n
                        
                    if is_front and cap_thick > 0:
                        in_bound.append(p - n * cap_thick)
                        cap_surf.append(p)
                    else:
                        # 後縁側または厚さ0の場合は表面から0.1mm外側に厚みを持たせて浮かせる
                        in_bound.append(p + n * 0.1)
                        cap_surf.append(p + n * (0.1 + t))
                        
                    out_bound.append(p + n * eps_out)
                
                rot_pts = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in in_bound + out_bound[::-1]]
                cap_geom = cap_surf + in_bound[::-1]
                rot_cap = [(pt - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y] for pt in cap_geom]
                
                try:
                    gp = Polygon(rot_pts).buffer(0)
                    if gp.is_valid and not gp.is_empty:
                        if is_front and cap_thick > 0: groove_polys.append(gp)
                        cap_pts_list.append(np.array(rot_cap))
                except Exception: pass
                
        build_cap(u_pts_rev, dist_u, True); build_cap(l_pts_rev, dist_l, False)
        if groove_polys:
            try: rib_poly = rib_poly.buffer(0).difference(unary_union(groove_polys).buffer(0)).buffer(0)
            except Exception: pass
            if getattr(rib_poly, 'geom_type', '') == 'MultiPolygon': rib_poly = max(rib_poly.geoms, key=lambda a: a.area)
        return rib_poly, cap_pts_list

    def find_intersection(self, x_start, y_start, slope, curve_x, curve_y, x_dir):
        x_end = np.min(curve_x) if x_dir == -1 else np.max(curve_x)
        eps = -0.1 if x_dir == -1 else 0.1
        if (x_dir == -1 and x_start + eps < x_end) or (x_dir == 1 and x_start + eps > x_end):
            return x_end, y_start + slope * (x_end - x_start)
            
        x_ray = np.linspace(x_start + eps, x_end, 500)
        y_ray = y_start + slope * (x_ray - x_start)
        diff = y_ray - np.interp(x_ray, curve_x, curve_y)
        
        signs = np.sign(diff)
        sign_changes = np.where(np.diff(signs) != 0)[0]
        
        if len(sign_changes) > 0:
            idx = sign_changes[0]
            x1, x2 = x_ray[idx], x_ray[idx+1]
            y1, y2 = diff[idx], diff[idx+1]
            x_int = x1 - y1 * (x2 - x1) / (y2 - y1) if y2 != y1 else x1
            return x_int, y_start + slope * (x_int - x_start)
        return x_end, y_start + slope * (x_end - x_start)

    def get_start_x(self, center_x, center_y, R_h_prot, R_v_prot, angle_deg, x_dir, start_upper, u_x, u_y, l_x, l_y, x_bound):
        x_curr = center_x
        to_upper = not start_upper
        if x_dir == 1:
            m = np.tan(np.radians(angle_deg)) if to_upper else -np.tan(np.radians(angle_deg))
        else:
            m = -np.tan(np.radians(angle_deg)) if to_upper else np.tan(np.radians(angle_deg))
        
        step = 0.5 * x_dir
        R_eff = np.sqrt((R_h_prot**2) * (m**2) + R_v_prot**2) / np.sqrt(m**2 + 1)
        while (x_dir == 1 and x_curr < x_bound) or (x_dir == -1 and x_curr > x_bound):
            y_curr = np.interp(x_curr, u_x, u_y) if start_upper else np.interp(x_curr, l_x, l_y)
            dist = abs(m * center_x - center_y - m * x_curr + y_curr) / np.sqrt(m**2 + 1)
            x_at_cy = x_curr + (center_y - y_curr) / m if m != 0 else x_curr
            
            if dist >= R_eff:
                if x_dir == 1 and x_at_cy >= center_x + R_h_prot: return x_curr
                if x_dir == -1 and x_at_cy <= center_x - R_h_prot: return x_curr
            x_curr += step
        return x_curr

    def generate_zigzag_raw(self, x_start, n_segments, x_dir, angle_deg, start_upper, u_x, u_y, l_x, l_y, x_bound):
        lines = []
        if n_segments <= 0: return lines
        cx = x_start
        cy = np.interp(cx, u_x, u_y) if start_upper else np.interp(cx, l_x, l_y)
        to_upper = not start_upper
        
        for _ in range(n_segments):
            if x_dir == 1:
                slope = np.tan(np.radians(angle_deg)) if to_upper else -np.tan(np.radians(angle_deg))
            else:
                slope = -np.tan(np.radians(angle_deg)) if to_upper else np.tan(np.radians(angle_deg))
                
            curve_x, curve_y = (u_x, u_y) if to_upper else (l_x, l_y)
            nx, ny = self.find_intersection(cx, cy, slope, curve_x, curve_y, x_dir)
            
            if abs(nx - cx) < 1.0 or (x_dir == 1 and nx > x_bound - 1.0) or (x_dir == -1 and nx < x_bound + 1.0):
                lines.append([(cx, cy), (nx, ny)])
                break
                
            lines.append([(cx, cy), (nx, ny)])
            cx, cy = nx, ny
            to_upper = not to_upper
        return lines

    def cut_polygon_by_line(self, poly, p1, p2, keep_side):
        try:
            poly = poly.buffer(0)
            if poly.is_empty: return poly
            p1, p2 = np.array(p1), np.array(p2)
            vec = p2 - p1
            length = np.linalg.norm(vec)
            if length == 0: return poly
            vec = vec / length
            
            extended_line = LineString([p1 - vec * 100000, p2 + vec * 100000])
            result = split(poly, extended_line)
        except Exception:
            return poly 

        geoms = list(result.geoms) if hasattr(result, 'geoms') else []
        if len(geoms) <= 1: return poly
            
        best_poly, best_val = None, -float('inf') if keep_side == 'right' else float('inf')
        for g in geoms:
            if getattr(g, 'geom_type', '') == 'Polygon':
                if (keep_side == 'right' and g.centroid.x > best_val) or (keep_side == 'left' and g.centroid.x < best_val):
                    best_val, best_poly = g.centroid.x, g
        return best_poly if best_poly else poly

    def process_blocks_sharp(self, blocks_f, blocks_r, R_mat, spar_x, spar_y, inner_poly, beam_width):
        sharp_polys = []
        if not inner_poly: return sharp_polys
        try: inner_poly = inner_poly.buffer(0)
        except Exception: return sharp_polys
        
        def process_side(blocks, is_rear):
            for b in blocks:
                if len(b) > 1:
                    rb = [( (np.array(l[0])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y], 
                            (np.array(l[1])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y] ) for l in b]
                    
                    c1, c2 = ('right', 'left') if is_rear else ('left', 'right')
                    canvas = self.cut_polygon_by_line(inner_poly, rb[0][0], rb[0][1], c1)
                    canvas = self.cut_polygon_by_line(canvas, rb[-1][0], rb[-1][1], c2)
                    
                    webs = []
                    for l in rb[1:-1]:
                        p1, p2 = np.array(l[0]), np.array(l[1])
                        vec = p2 - p1
                        if np.linalg.norm(vec) > 0:
                            vec = vec / np.linalg.norm(vec)
                            w_line = LineString([p1 - vec * 10000, p2 + vec * 10000])
                            try: webs.append(w_line.buffer(beam_width / 2.0).buffer(0))
                            except Exception: pass
                            
                    if webs: 
                        try:
                            safe_webs = unary_union(webs).buffer(0)
                            canvas = canvas.buffer(0).difference(safe_webs).buffer(0)
                        except Exception: pass
                    
                    polys = [p for p in ([canvas] if getattr(canvas, 'geom_type', '') == 'Polygon' else list(getattr(canvas, 'geoms', [])))
                             if getattr(p, 'geom_type', '') == 'Polygon' and p.area > 5.0]
                    polys.sort(key=lambda p: abs(p.centroid.x - spar_x))
                    for idx, p in enumerate(polys):
                        sharp_polys.append((p, is_rear, idx))

        process_side(blocks_f, is_rear=False)
        process_side(blocks_r, is_rear=True)
        return sharp_polys

    def interpolate_leading_edge(self, u_x, u_y, l_x, l_y, chord, rng_pct, divisions):
        import scipy.interpolate
        
        x_thresh = (rng_pct / 100.0) * chord
        
        u_mask = u_x <= x_thresh
        l_mask = l_x <= x_thresh
        
        l_x_sub = l_x[l_mask][::-1]
        l_y_sub = l_y[l_mask][::-1]
        
        u_x_sub = u_x[u_mask][1:]
        u_y_sub = u_y[u_mask][1:]
        
        x_sub = np.concatenate((l_x_sub, u_x_sub))
        y_sub = np.concatenate((l_y_sub, u_y_sub))
        
        if len(x_sub) < 4:
            return u_x, u_y, l_x, l_y
            
        dx = np.diff(x_sub)
        dy = np.diff(y_sub)
        dist = np.sqrt(dx**2 + dy**2)
        t = np.concatenate(([0], np.cumsum(dist)))
        if t[-1] == 0: return u_x, u_y, l_x, l_y
        t /= t[-1]
        
        spline_x = scipy.interpolate.CubicSpline(t, x_sub)
        spline_y = scipy.interpolate.CubicSpline(t, y_sub)
        
        t_new = np.linspace(0, 1, int(divisions))
        x_new = spline_x(t_new)
        y_new = spline_y(t_new)
        
        le_idx = np.argmin(x_new)
        
        new_l_x = x_new[:le_idx+1][::-1]
        new_l_y = y_new[:le_idx+1][::-1]
        
        new_u_x = x_new[le_idx:]
        new_u_y = y_new[le_idx:]
        
        final_u_x = np.concatenate((new_u_x, u_x[~u_mask]))
        final_u_y = np.concatenate((new_u_y, u_y[~u_mask]))
        
        final_l_x = np.concatenate((new_l_x, l_x[~l_mask]))
        final_l_y = np.concatenate((new_l_y, l_y[~l_mask]))
        
        return final_u_x, final_u_y, final_l_x, final_l_y

    def generate_single_rib(self, p: RibParameters) -> RibGenerationResult:
        file1 = p.file1
        file2 = p.file2
        blend_ratio = p.blend_ratio
        chord = p.chord
        spar_pct = p.spar_pct
        washout_deg = p.washout_deg
        spar_hole_dia = p.spar_hole_dia
        spar_hole_dv = p.spar_hole_dv
        rear_dx = p.rear_dx
        rear_dy = p.rear_dy
        rear_dia = p.rear_dia
        front_dx = p.front_dx
        front_dy = p.front_dy
        front_dia = p.front_dia
        truss_angle = p.truss_angle
        truss_front_n = p.truss_front_n
        truss_rear_n = p.truss_rear_n
        truss_scale_front_list = p.truss_scale_front_list
        truss_scale_rear_list = p.truss_scale_rear_list
        beam_width = p.beam_width
        margin_spar = p.margin_spar
        margin_bolt = p.margin_bolt
        margin_outer = p.margin_outer
        truss_fillet = p.truss_fillet
        min_hole_dia = p.min_hole_dia
        xb_t_list = p.xb_t_list
        x_dia = p.x_dia
        plank_start = p.plank_start
        plank_end = p.plank_end
        plank_part_start = p.plank_part_start
        plank_part_end = p.plank_part_end
        plank_thick = p.plank_thick
        stringers_data = p.stringers_data
        te_cut = p.te_cut
        apply_safe_margin = p.apply_safe_margin
        te_cap_uf_act = p.te_cap_uf_act
        te_cap_uf_w = p.te_cap_uf_w
        te_cap_ur_act = p.te_cap_ur_act
        te_cap_ur_w = p.te_cap_ur_w
        te_cap_lf_act = p.te_cap_lf_act
        te_cap_lf_w = p.te_cap_lf_w
        te_cap_lr_act = p.te_cap_lr_act
        te_cap_lr_w = p.te_cap_lr_w
        te_cap_thick = p.te_cap_thick
        rc1_act = p.rc1_act
        rc1_start = p.rc1_start
        rc1_end = p.rc1_end
        rc1_thick = p.rc1_thick
        rc2_act = p.rc2_act
        rc2_start = p.rc2_start
        rc2_end = p.rc2_end
        rc2_thick = p.rc2_thick
        bolt1_dx = p.bolt1_dx
        bolt1_dy = p.bolt1_dy
        bolt1_dia = p.bolt1_dia
        bolt2_dx = p.bolt2_dx
        bolt2_dy = p.bolt2_dy
        bolt2_dia = p.bolt2_dia
        diag_params_list = p.diag_params_list
        fast_mode = p.fast_mode
        tabs_active = p.tabs_active
        truss_tab_width = p.truss_tab_width
        
        tab_centers = []
        warnings_list = []
        pts1 = self.load_dat(file1)
        pts2 = self.load_dat(file2)

        n_pts = 300
        blended = self.resample_airfoil(pts1, n_pts) * (1.0 - blend_ratio) + self.resample_airfoil(pts2, n_pts) * blend_ratio
        scaled = blended * chord

        le_idx = np.argmin(scaled[:, 0])
        u_x_orig, u_y_orig = scaled[:le_idx+1, 0][::-1], scaled[:le_idx+1, 1][::-1]
        l_x_orig, l_y_orig = scaled[le_idx:, 0], scaled[le_idx:, 1]
        
        if p.le_interp_active:
            u_x_orig, u_y_orig, l_x_orig, l_y_orig = self.interpolate_leading_edge(
                u_x_orig, u_y_orig, l_x_orig, l_y_orig, chord, p.le_interp_range, p.le_interp_divisions
            )
        
        spar_x = chord * (spar_pct / 100.0)
        spar_y = (np.interp(spar_x, u_x_orig, u_y_orig) + np.interp(spar_x, l_x_orig, l_y_orig)) / 2.0

        w_theta = np.radians(washout_deg)
        R_mat = np.array([[np.cos(w_theta), -np.sin(w_theta)], [np.sin(w_theta), np.cos(w_theta)]])
        
        final_rib_orig = (scaled - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        u_x_mod, u_y_mod, l_x_mod, l_y_mod, plank_poly_unrot = self.apply_plank_offset(u_x_orig, u_y_orig, l_x_orig, l_y_orig, plank_start, plank_end, plank_part_start, plank_part_end, plank_thick, chord)
        
        scaled_mod = np.vstack((
            np.column_stack((u_x_mod[::-1], u_y_mod[::-1])),
            np.column_stack((l_x_mod[1:], l_y_mod[1:]))
        ))
        final_rib_mod = (scaled_mod - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        plank_poly_rot = []
        if len(plank_poly_unrot) > 0:
            plank_poly_rot = (plank_poly_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        P_u_rot, P_l_rot = None, None
        P_u_rot_te, P_l_rot_te = None, None
        if te_cut > 0:
            u_pts_rev = np.column_stack((u_x_orig[::-1], u_y_orig[::-1]))
            dist_u = np.zeros(len(u_pts_rev))
            dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))
            
            l_pts_rev = np.column_stack((l_x_orig[::-1], l_y_orig[::-1]))
            dist_l = np.zeros(len(l_pts_rev))
            dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))
            
            cut_u_x = np.interp(te_cut, dist_u, u_pts_rev[:, 0])
            cut_u_y = np.interp(te_cut, dist_u, u_pts_rev[:, 1])
            cut_l_x = np.interp(te_cut, dist_l, l_pts_rev[:, 0])
            cut_l_y = np.interp(te_cut, dist_l, l_pts_rev[:, 1])
            
            P_u_rot = (np.array([cut_u_x, cut_u_y]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
            P_l_rot = (np.array([cut_l_x, cut_l_y]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

            te_cut_overlap = te_cut + 10.0
            cut_u_x_te = np.interp(te_cut_overlap, dist_u, u_pts_rev[:, 0])
            cut_u_y_te = np.interp(te_cut_overlap, dist_u, u_pts_rev[:, 1])
            cut_l_x_te = np.interp(te_cut_overlap, dist_l, l_pts_rev[:, 0])
            cut_l_y_te = np.interp(te_cut_overlap, dist_l, l_pts_rev[:, 1])

            P_u_rot_te = (np.array([cut_u_x_te, cut_u_y_te]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
            P_l_rot_te = (np.array([cut_l_x_te, cut_l_y_te]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        c_m = np.array([spar_x, spar_y])
        c_b1_unrot = np.array([spar_x + bolt1_dx, spar_y + bolt1_dy])
        c_b2_unrot = np.array([spar_x + bolt2_dx, spar_y + bolt2_dy])
        c_b1 = (c_b1_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        c_b2 = (c_b2_unrot - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        c_f = (np.array([spar_x + front_dx, spar_y + front_dy]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]
        c_r = (np.array([spar_x + rear_dx, spar_y + rear_dy]) - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        stringer_pts_list = []
        te_cap_pts_list = []
        rc_cap_pts_list = []

        if SHAPELY_AVAILABLE:
            try: final_rib_mod_poly = Polygon(final_rib_mod).buffer(0)
            except: final_rib_mod_poly = None
            
            for st in stringers_data:
                st['dxf_pts'] = self.load_dxf_profile(st['dxf_path']) if st['use_dxf'] else None
                
            if final_rib_mod_poly:
                final_rib_mod_poly, stringer_pts_list = self.apply_stringer_grooves(
                    final_rib_mod_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig, 
                    chord, spar_x, spar_y, R_mat, stringers_data,
                    plank_start, plank_end, plank_thick
                )
            
            if final_rib_mod_poly and (te_cap_uf_act or te_cap_ur_act or te_cap_lf_act or te_cap_lr_act):
                final_rib_mod_poly, te_cap_pts_list = self.apply_te_caps(
                    final_rib_mod_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig,
                    te_cut, te_cap_thick, spar_x, spar_y, R_mat,
                    te_cap_uf_act, te_cap_uf_w, te_cap_ur_act, te_cap_ur_w,
                    te_cap_lf_act, te_cap_lf_w, te_cap_lr_act, te_cap_lr_w
                )
            
            if final_rib_mod_poly and (rc1_act or rc2_act):
                final_rib_mod_poly, rc_cap_pts_tuple = self.apply_rib_caps(
                    final_rib_mod_poly, u_x_orig, u_y_orig, l_x_orig, l_y_orig,
                    chord, spar_x, spar_y, R_mat,
                    rc1_act, rc1_start, rc1_end, rc1_thick,
                    rc2_act, rc2_start, rc2_end, rc2_thick
                )
                rc_cap_pts_list = rc_cap_pts_tuple
            else:
                rc_cap_pts_list = ([], [])
            
            te_part_coords = []
            if final_rib_mod_poly and P_u_rot is not None and P_l_rot is not None:
                main_poly = self.cut_polygon_by_line(final_rib_mod_poly, P_u_rot, P_l_rot, 'left')
                te_poly = self.cut_polygon_by_line(final_rib_mod_poly, P_u_rot_te, P_l_rot_te, 'right')
                final_rib_mod_poly = main_poly
                if getattr(te_poly, 'is_empty', True) == False:
                    te_part_coords = np.array(te_poly.exterior.coords)
                    
            # Removed vertical spar tab logic as it is replaced by E-shape supports in cam_engine.py

            final_rib_mod = np.array(final_rib_mod_poly.exterior.coords) if final_rib_mod_poly and not final_rib_mod_poly.is_empty else []
        else:
            te_part_coords = []
            final_rib_mod_poly = None

        u_x_guide, u_y_guide = self.get_smoothed_guideline(u_x_orig, u_y_orig, chord, plank_start, plank_end, plank_thick, True)
        l_x_guide, l_y_guide = self.get_smoothed_guideline(l_x_orig, l_y_orig, chord, plank_start, plank_end, plank_thick, False)
        
        scaled_guide = np.vstack((
            np.column_stack((u_x_guide[::-1], u_y_guide[::-1])),
            np.column_stack((l_x_guide[1:], l_y_guide[1:]))
        ))
        final_rib_guide = (scaled_guide - [spar_x, spar_y]).dot(R_mat.T) + [spar_x, spar_y]

        inner_poly_canvas = None
        if SHAPELY_AVAILABLE and final_rib_mod_poly:
            try:
                if apply_safe_margin:
                    temp_canvas = Polygon(final_rib_guide).buffer(-margin_outer).buffer(0)
                else:
                    temp_canvas = final_rib_mod_poly.buffer(-margin_outer).buffer(0)
                    
                if temp_canvas.is_empty:
                    warnings_list.append("Outer Margin is too large! Trusses cannot be generated.")
                elif getattr(temp_canvas, 'geom_type', '') == 'MultiPolygon':
                    inner_poly_canvas = max(temp_canvas.geoms, key=lambda a: a.area)
                elif getattr(temp_canvas, 'geom_type', '') == 'Polygon':
                    inner_poly_canvas = temp_canvas
            except Exception:
                warnings_list.append("Error calculating inner truss canvas.")

        minx_guide = min(np.min(u_x_guide), np.min(l_x_guide))
        maxx_guide = max(np.max(u_x_guide), np.max(l_x_guide))
        
        dh_prot = spar_hole_dia/2.0 + margin_spar
        dv_prot = spar_hole_dv/2.0 + margin_spar if spar_hole_dv >= 0 else dh_prot

        start_x_f = self.get_start_x(spar_x, spar_y, dh_prot, dv_prot, truss_angle, -1, False, u_x_guide, u_y_guide, l_x_guide, l_y_guide, minx_guide)
        b_f_ideal = self.generate_zigzag_raw(start_x_f, truss_front_n + 1, -1, truss_angle, False, u_x_guide, u_y_guide, l_x_guide, l_y_guide, minx_guide)
        blocks_f = [b_f_ideal] if b_f_ideal else []

        start_x_r = self.get_start_x(spar_x, spar_y, dh_prot, dv_prot, truss_angle, 1, True, u_x_guide, u_y_guide, l_x_guide, l_y_guide, maxx_guide)
        b_r_ideal = self.generate_zigzag_raw(start_x_r, truss_rear_n + 1, 1, truss_angle, True, u_x_guide, u_y_guide, l_x_guide, l_y_guide, maxx_guide)
        blocks_r = [b_r_ideal] if b_r_ideal else []
        
        if inner_poly_canvas and P_u_rot is not None and P_l_rot is not None:
            inner_poly_canvas = self.cut_polygon_by_line(inner_poly_canvas, P_u_rot, P_l_rot, 'left')
            
        h_polys_sharp = self.process_blocks_sharp(blocks_f, blocks_r, R_mat, spar_x, spar_y, inner_poly_canvas, beam_width)

        active_xbs, skipped_xbs, active_obs_list = [], [], []
        diag_poly_pts_list = []
        
        if SHAPELY_AVAILABLE:
            def safe_buffer_obs(geom_pt, radius):
                try:
                    b = geom_pt.buffer(radius).buffer(0)
                    if not b.is_empty and b.is_valid: return b
                except: pass
                return None

            if bolt1_dia >= 0:
                b_b1 = safe_buffer_obs(Point(c_b1), bolt1_dia/2.0 + margin_bolt)
                if b_b1: active_obs_list.append(b_b1)
            if bolt2_dia >= 0:
                b_b2 = safe_buffer_obs(Point(c_b2), bolt2_dia/2.0 + margin_bolt)
                if b_b2: active_obs_list.append(b_b2)
            if spar_hole_dia >= 0:
                # 楕円穴ポリゴンを生成（margin_spar分膨らませる）
                theta_c = np.linspace(0, 2 * np.pi, 100)
                dh = spar_hole_dia
                dv = spar_hole_dv if spar_hole_dv >= 0 else dh
                ellipse_m = np.column_stack((c_m[0] + dh/2*np.cos(theta_c), c_m[1] + dv/2*np.sin(theta_c)))
                b_m = safe_buffer_obs(Polygon(ellipse_m), margin_spar)
                if b_m: active_obs_list.append(b_m)
            if front_dia >= 0:
                b_f = safe_buffer_obs(Point(c_f), front_dia/2.0 + margin_spar)
                if b_f: active_obs_list.append(b_f)
            if rear_dia >= 0:
                b_r = safe_buffer_obs(Point(c_r), rear_dia/2.0 + margin_spar)
                if b_r: active_obs_list.append(b_r)
            
            if x_dia >= 0:
                vec = c_r - c_m
                dist_L = np.linalg.norm(vec)
                if dist_L > 0:
                    u = vec / dist_L
                    len_L = dist_L - (spar_hole_dia/2.0 + rear_dia/2.0)
                    center_L = c_m + u * (spar_hole_dia/2.0 + len_L/2.0)
                    xb_centers_abs = []
                    for t in xb_t_list:
                        offset = (len_L / 2.0) * (abs(0.5 - t) * 2.0)
                        if t <= 0.5:
                            xb_centers_abs.append(center_L - u * offset)
                        else:
                            xb_centers_abs.append(center_L + u * offset)

                    
                    for ct in xb_centers_abs:
                        try:
                            xb_poly = Point(ct).buffer(x_dia/2.0).buffer(0)
                            xb_obs = Point(ct).buffer(x_dia/2.0 + margin_outer).buffer(0)
                            if xb_poly.is_valid and xb_obs.is_valid:
                                xb = {'abs_ct': ct, 'poly': xb_poly, 'obs': xb_obs}
                                is_contained = False
                                for p, _, _ in h_polys_sharp:
                                    try:
                                        if p.contains(xb_poly):
                                            is_contained = True
                                            break
                                    except: pass
                                if is_contained: skipped_xbs.append(xb) 
                                else: active_xbs.append(xb); active_obs_list.append(xb_obs)
                        except: pass
            
            if diag_params_list:
                for diag_params in diag_params_list:
                    try:
                        vec = c_r - c_m
                        dist_L = np.linalg.norm(vec)
                        if dist_L > 0:
                            u = vec / dist_L
                            P_start = c_m + u * (spar_hole_dia / 2.0)
                            P_end = c_r - u * (rear_dia / 2.0)
                            
                            t1 = diag_params['t1']
                            t2 = diag_params['t2']
                            R_diag = diag_params['R']
                            t_thick = diag_params['t']
                            
                            C1 = P_start + t1 * (P_end - P_start)
                            C2 = P_start + t2 * (P_end - P_start)
                            
                            L_C = np.linalg.norm(C2 - C1)
                            if L_C < 1e-5:
                                diag_poly = Point(C1).buffer(R_diag).buffer(0)
                            else:
                                u_c = (C2 - C1) / L_C
                                if t_thick <= 1e-5:
                                    S = 0
                                else:
                                    S = R_diag * (np.sqrt(L_C**2 + t_thick**2) / t_thick - 1)
                                E1 = C1 - u_c * S
                                E2 = C2 + u_c * S
                                diag_poly = LineString([E1, E2]).buffer(R_diag).buffer(0)
                                
                            if diag_poly and diag_poly.is_valid and not diag_poly.is_empty:
                                if getattr(diag_poly, 'geom_type', '') == 'Polygon':
                                    diag_pts = np.array(diag_poly.exterior.coords)
                                elif getattr(diag_poly, 'geom_type', '') == 'MultiPolygon':
                                    diag_poly = max(diag_poly.geoms, key=lambda a: a.area)
                                    diag_pts = np.array(diag_poly.exterior.coords)
                                else:
                                    diag_pts = []
                                
                                if len(diag_pts) > 0:
                                    diag_poly_pts_list.append(diag_pts)
                                
                                diag_obs = diag_poly.buffer(margin_outer).buffer(0)
                                if not diag_obs.is_empty:
                                    active_obs_list.append(diag_obs)
                    except Exception:
                        pass

            if apply_safe_margin and final_rib_mod_poly:
                try:
                    poly_c = Polygon(final_rib_guide).buffer(-margin_outer).buffer(0)
                    poly_a = final_rib_mod_poly.buffer(-margin_outer).buffer(0)
                    if P_u_rot is not None and P_l_rot is not None:
                        poly_c = self.cut_polygon_by_line(poly_c, P_u_rot, P_l_rot, 'left')
                        poly_a = self.cut_polygon_by_line(poly_a, P_u_rot, P_l_rot, 'left')
                        
                    if not poly_c.is_empty and not poly_a.is_empty:
                        gouges = poly_c.difference(poly_a).buffer(0)
                        for g in (gouges.geoms if getattr(gouges, 'geom_type', '') in ('MultiPolygon', 'GeometryCollection') else [gouges]):
                            if getattr(g, 'geom_type', '') == 'Polygon' and g.area > 0.1 and g.area < poly_c.area * 0.2:
                                active_obs_list.append(g.simplify(0.1).buffer(0))
                except Exception:
                    pass

        final_sharp_polys = []
        if not fast_mode and active_obs_list and SHAPELY_AVAILABLE:
            cleaned_obs = []
            for o in active_obs_list:
                try:
                    c_o = o.buffer(0).simplify(0.01).buffer(0)
                    if not c_o.is_empty and getattr(c_o, 'geom_type', '') in ('Polygon', 'MultiPolygon'): 
                        cleaned_obs.append(c_o)
                except: pass
                
            for raw_p, is_rear, b_idx in h_polys_sharp:
                try: p = raw_p.buffer(0)
                except: continue
                
                if getattr(p, 'geom_type', '') == 'MultiPolygon': p = max(p.geoms, key=lambda a: a.area)
                if p.is_empty or getattr(p, 'geom_type', '') != 'Polygon': continue

                hit_obs = []
                for obs in cleaned_obs:
                    try:
                        if p.intersection(obs).area > 0.1: hit_obs.append(obs)
                    except Exception:
                        hit_obs.append(obs)

                if not hit_obs:
                    final_sharp_polys.append((p, is_rear, b_idx))
                    continue

                best_scaled_p = None
                best_scaled_area = 0
                
                coords = list(p.exterior.coords)
                anchors = [Point(c) for c in coords]
                try: anchors.append(p.centroid)
                except: pass
                
                for i in range(len(coords)-1):
                    mx = (coords[i][0] + coords[i+1][0]) / 2.0
                    my = (coords[i][1] + coords[i+1][1]) / 2.0
                    anchors.append(Point(mx, my))
                
                try:
                    obs_union = unary_union(hit_obs)
                    obs_center = obs_union.centroid
                except:
                    obs_center = Point(0, 0)
                
                def get_dist(anchor):
                    try: return anchor.distance(obs_center)
                    except: return 0.0
                anchors.sort(key=get_dist, reverse=True)

                best_k = 0.05
                for anchor in anchors:
                    low = max(0.05, best_k)
                    high = 1.0
                    ans_k = None
                    ans_poly = None
                    
                    while high - low > 0.01:
                        mid = (low + high) / 2.0
                        try:
                            p_scaled = scale(p, xfact=mid, yfact=mid, origin=anchor).buffer(0)
                            if p_scaled.is_empty or getattr(p_scaled, 'geom_type', '') != 'Polygon':
                                high = mid
                                continue
                            
                            intersects = False
                            for o in hit_obs:
                                try:
                                    if p_scaled.intersection(o).area > 0.1:
                                        intersects = True
                                        break
                                except Exception:
                                    intersects = True
                                    break
                            
                            if intersects:
                                high = mid
                            else:
                                low = mid
                                ans_k = mid
                                ans_poly = p_scaled
                        except Exception:
                            high = mid
                    
                    if ans_poly and ans_k and ans_poly.area > best_scaled_area:
                        if min_hole_dia > 0:
                            try:
                                core = ans_poly.buffer(-min_hole_dia / 2.0).buffer(0)
                                if not core.is_empty and getattr(core, 'geom_type', '') in ('Polygon', 'MultiPolygon'):
                                    best_scaled_area = ans_poly.area
                                    best_scaled_p = ans_poly
                                    best_k = ans_k
                            except Exception: pass
                        else:
                            best_scaled_area = ans_poly.area
                            best_scaled_p = ans_poly
                            best_k = ans_k 

                if best_scaled_p and best_scaled_area > 5.0:
                    final_sharp_polys.append((best_scaled_p, is_rear, b_idx))
        else:
            final_sharp_polys = h_polys_sharp

        final_truss_holes = []
        if SHAPELY_AVAILABLE:
            def add_truss_hole_with_tabs(poly):
                if not tabs_active or not poly or poly.is_empty:
                    final_truss_holes.append(np.array(poly.exterior.coords))
                    return
                try:
                    coords = list(poly.exterior.coords)
                    if len(coords) < 3:
                        final_truss_holes.append(np.array(poly.exterior.coords))
                        return
                        
                    pts = np.array(coords)
                    for i in range(len(pts) - 1):
                        p1 = pts[i]
                        p2 = pts[i+1]
                        segment_len = np.sqrt(np.sum((p2 - p1)**2))
                        if segment_len >= 4.0 * truss_tab_width:
                            p_mid = (p1 + p2) / 2.0
                            tab_centers.append((float(p_mid[0]), float(p_mid[1])))
                    
                    final_truss_holes.append(np.array(poly.exterior.coords))
                except Exception:
                    final_truss_holes.append(np.array(poly.exterior.coords))

            for p_data in final_sharp_polys:
                try:
                    p, is_rear, b_idx = p_data
                    p_clean = p.buffer(0)
                    if p_clean.is_empty: continue
                    
                    scale_list = truss_scale_rear_list if is_rear else truss_scale_front_list
                    factor = scale_list[b_idx] if b_idx < len(scale_list) else 1.0
                    if factor != 1.0:
                        import math
                        r_approx = math.sqrt(p_clean.area / math.pi)
                        offset_val = r_approx * (1.0 - factor)
                        p_clean = p_clean.buffer(-offset_val).buffer(0)
                        if p_clean.is_empty: continue

                    if truss_fillet > 0:
                        rp = p_clean.buffer(-truss_fillet).buffer(truss_fillet).buffer(0)
                        if getattr(rp, 'geom_type', '') == 'Polygon' and rp.area > 0.1:
                            if not fast_mode and min_hole_dia > 0 and rp.buffer(-min_hole_dia / 2.0).is_empty:
                                continue
                            add_truss_hole_with_tabs(rp)
                        elif getattr(rp, 'geom_type', '') == 'MultiPolygon':
                            for sub_p in rp.geoms:
                                if sub_p.area > 0.1:
                                    if not fast_mode and min_hole_dia > 0 and sub_p.buffer(-min_hole_dia / 2.0).is_empty:
                                        continue
                                    add_truss_hole_with_tabs(sub_p)
                    else:
                        if not fast_mode and min_hole_dia > 0 and p_clean.buffer(-min_hole_dia / 2.0).is_empty:
                            continue
                        add_truss_hole_with_tabs(p_clean)
                except Exception:
                    pass

        if SHAPELY_AVAILABLE and final_rib_mod_poly:
            try:
                poly_mod = Polygon(final_rib_mod).buffer(0)
                if not poly_mod.is_valid:
                    warnings_list.append("Rib shape self-intersects! (Check Plank/Stringer settings)")
            except:
                warnings_list.append("Rib shape is invalid!")

        theta_c = np.linspace(0, 2 * np.pi, 100)
        hole_m = np.column_stack((c_m[0] + spar_hole_dia/2*np.cos(theta_c), c_m[1] + spar_hole_dv/2*np.sin(theta_c))) if spar_hole_dia > 0 and len(c_m) >= 2 else []
        hole_r = np.column_stack((c_r[0] + rear_dia/2*np.cos(theta_c), c_r[1] + rear_dia/2*np.sin(theta_c))) if rear_dia > 0 and len(c_r) >= 2 else []
        hole_f = np.column_stack((c_f[0] + front_dia/2*np.cos(theta_c), c_f[1] + front_dia/2*np.sin(theta_c))) if front_dia > 0 and len(c_f) >= 2 else []
        hole_b1 = np.column_stack((c_b1[0] + bolt1_dia/2*np.cos(theta_c), c_b1[1] + bolt1_dia/2*np.sin(theta_c))) if bolt1_dia > 0 and len(c_b1) >= 2 else []
        hole_b2 = np.column_stack((c_b2[0] + bolt2_dia/2*np.cos(theta_c), c_b2[1] + bolt2_dia/2*np.sin(theta_c))) if bolt2_dia > 0 and len(c_b2) >= 2 else []
        
        xb_r_active = [np.column_stack((xb['abs_ct'][0] + x_dia/2*np.cos(theta_c), xb['abs_ct'][1] + x_dia/2*np.sin(theta_c))) for xb in active_xbs if len(xb['abs_ct']) >= 2] if x_dia > 0 else []
        xb_r_skipped = [np.column_stack((xb['abs_ct'][0] + x_dia/2*np.cos(theta_c), xb['abs_ct'][1] + x_dia/2*np.sin(theta_c))) for xb in skipped_xbs if len(xb['abs_ct']) >= 2] if x_dia > 0 else []

        # --- Hole Boundary Collision Check ---
        if SHAPELY_AVAILABLE and final_rib_mod_poly:
            try:
                poly_mod = Polygon(final_rib_mod).buffer(0)
                
                def check_hole(pts, name):
                    if len(pts) > 0:
                        try:
                            h_poly = Polygon(pts)
                            # 完全に中(within)でもなく、完全に外(disjoint)でもない場合(境界と交差・一部はみ出し)
                            if not h_poly.within(poly_mod) and not h_poly.disjoint(poly_mod):
                                warnings_list.append(f"WARNING: {name} intersects rib boundary!")
                        except:
                            pass
                            
                check_hole(hole_m, "Main Spar")
                check_hole(hole_r, "Rear Spar")
                check_hole(hole_f, "Front Spar")
                check_hole(hole_b1, "Bolt 1")
                check_hole(hole_b2, "Bolt 2")
                
                for i, xb_pts in enumerate(xb_r_active):
                    check_hole(xb_pts, f"X-Brace({i+1})")
            except Exception:
                pass

        return RibGenerationResult(
            final_rib_mod, c_m, hole_m, c_r, hole_r, c_f, hole_f, final_truss_holes, 
            xb_r_active, [xb['abs_ct'] for xb in active_xbs], xb_r_skipped, [xb['abs_ct'] for xb in skipped_xbs], 
            warnings_list, plank_poly_rot, te_part_coords, c_b1, hole_b1, c_b2, hole_b2, 
            diag_poly_pts_list, final_rib_orig, stringer_pts_list, te_cap_pts_list, rc_cap_pts_list,
            tab_centers
        )

    def get_local_params(self, p: Dict[str, Any], y_local: float) -> Tuple[float, float, float, float, float, float]:
        y_global = y_local + p['joint_length']
        t = y_local / p['wing_span'] if p['wing_span'] > 0 else 0
        chord = max(p['chord_root'] * (1 - t) + p['chord_tip'] * t, 1.0)  # Prevent extremely small/zero chords
        spar_pct = p['spar_pos_root'] * (1 - t) + p['spar_pos_tip'] * t
        base_aoa = p.get('base_aoa', 0.0)
        washout_root = p.get('washout_root', 0.0)
        washout_tip = p.get('washout_tip', 0.0)
        washout_exp = p.get('washout_exp', 1.0)
        washout = base_aoa + washout_root + (washout_tip - washout_root) * (t ** washout_exp)
        
        xb_t_list = []
        x_dia = 0.0
        for start, end, offset in p['xb_zones']:
            if start is not None and end is not None:
                # Wire 1: Main (start - offset) to Rear (end)
                m1_y = start - offset
                r1_y = end
                if (m1_y <= y_global <= r1_y) or (r1_y <= y_global <= m1_y):
                    t1 = (y_global - m1_y) / (r1_y - m1_y) if r1_y != m1_y else 0.5
                    xb_t_list.append(t1)
                    x_dia = p['xbrace_dia']

                # Wire 2: Main (end + offset) to Rear (start)
                m2_y = end + offset
                r2_y = start
                if (m2_y <= y_global <= r2_y) or (r2_y <= y_global <= m2_y):
                    t2 = (y_global - m2_y) / (r2_y - m2_y) if r2_y != m2_y else 0.5
                    xb_t_list.append(t2)
                    x_dia = p['xbrace_dia']

        return chord, spar_pct, washout, t, xb_t_list, x_dia

    def generate_rib_at_y(self, p: Dict[str, Any], y_local: float, rib_index: int, thickness: float, is_carbon: bool = False, te_cut_override: float = None) -> Tuple[Any, ...]:
        y_global = y_local + p['joint_length']
        chord, spar_pct, washout, blend, xb_t_list, x_dia = self.get_local_params(p, y_local)
        angle = p['truss_angles_dict'].get(rib_index, p['base_truss_angle'])
        is_root, is_tip = (rib_index == 0), (rib_index == len(p['y_positions']) - 1)
        
        active_margin = p['margin_outer_edge'] if is_root or is_tip else p['margin_outer']
        active_beam = p['edge_beam_width'] if is_root or is_tip else p['beam_width']
        
        b1 = p['root_bolt1'] if is_root else (p['tip_bolt1'] if is_tip else (0,0,-1.0))
        b2 = p['root_bolt2'] if is_root else (p['tip_bolt2'] if is_tip else (0,0,-1.0))
        if None in b1: b1 = (0.0, 0.0, -1.0)
        if None in b2: b2 = (0.0, 0.0, -1.0)

        te_cut_val = te_cut_override if te_cut_override is not None else p['te_cut']

        diag_params = []
        if p.get('diag1_active') and p.get('diag1_range') and p['diag1_range'][0] <= y_global + thickness and y_global <= p['diag1_range'][1]:
            t1 = (y_global - p['diag1_y_main']) / (p['diag1_y_rear'] - p['diag1_y_main'])
            t2 = (y_global + thickness - p['diag1_y_main']) / (p['diag1_y_rear'] - p['diag1_y_main'])
            diag_params.append({'t1': t1, 't2': t2, 'R': p['rear_spar_dia'] / 2.0, 't': thickness})
        if p.get('diag2_active') and p.get('diag2_range') and p['diag2_range'][0] <= y_global + thickness and y_global <= p['diag2_range'][1]:
            t1 = (y_global - p['diag2_y_main']) / (p['diag2_y_rear'] - p['diag2_y_main'])
            t2 = (y_global + thickness - p['diag2_y_main']) / (p['diag2_y_rear'] - p['diag2_y_main'])
            diag_params.append({'t1': t1, 't2': t2, 'R': p['rear_spar_dia'] / 2.0, 't': thickness})

        # Calculate interpolated positions for spars
        front_dx_root = p.get('front_spar_dx_root')
        if front_dx_root is None: front_dx_root = p.get('front_spar_dx')
        front_dx_tip = p.get('front_spar_dx_tip')
        if front_dx_tip is None: front_dx_tip = p.get('front_spar_dx')
        front_dy_root = p.get('front_spar_dy_root')
        if front_dy_root is None: front_dy_root = p.get('front_spar_dy')
        front_dy_tip = p.get('front_spar_dy_tip')
        if front_dy_tip is None: front_dy_tip = p.get('front_spar_dy')
        
        if None in (front_dx_root, front_dx_tip, front_dy_root, front_dy_tip):
            p['front_spar_dia'] = -1.0
            front_dx_root = front_dx_tip = front_dy_root = front_dy_tip = 0.0

        front_dx = front_dx_root * (1 - blend) + front_dx_tip * blend
        front_dy = front_dy_root * (1 - blend) + front_dy_tip * blend

        rear_dx_root = p.get('rear_spar_dx_root')
        if rear_dx_root is None: rear_dx_root = p.get('rear_spar_dx')
        rear_dx_tip = p.get('rear_spar_dx_tip')
        if rear_dx_tip is None: rear_dx_tip = p.get('rear_spar_dx')
        rear_dy_root = p.get('rear_spar_dy_root')
        if rear_dy_root is None: rear_dy_root = p.get('rear_spar_dy')
        rear_dy_tip = p.get('rear_spar_dy_tip')
        if rear_dy_tip is None: rear_dy_tip = p.get('rear_spar_dy')

        if None in (rear_dx_root, rear_dx_tip, rear_dy_root, rear_dy_tip):
            p['rear_spar_dia'] = -1.0
            rear_dx_root = rear_dx_tip = rear_dy_root = rear_dy_tip = 0.0

        rear_dx = rear_dx_root * (1 - blend) + rear_dx_tip * blend
        rear_dy = rear_dy_root * (1 - blend) + rear_dy_tip * blend

        params_obj = RibParameters(
            file1=p['file1'], file2=p['file2'], blend_ratio=blend, chord=chord, spar_pct=spar_pct, washout_deg=washout,
            spar_hole_dia=p['spar_hole_dia'], spar_hole_dv=p.get('spar_hole_dv', 0.0) or p['spar_hole_dia'], rear_dx=rear_dx, rear_dy=rear_dy, rear_dia=p['rear_spar_dia'],
            front_dx=front_dx, front_dy=front_dy, front_dia=p['front_spar_dia'],
            truss_angle=angle, truss_front_n=p['truss_front_n'], truss_rear_n=p['truss_rear_n'],
            truss_scale_front_list=[float(x) for x in str(p.get('truss_scale_front', '')).split(',') if x.strip()],
            truss_scale_rear_list=[float(x) for x in str(p.get('truss_scale_rear', '')).split(',') if x.strip()],
            beam_width=active_beam, margin_spar=p['margin_spar'], margin_bolt=p['margin_bolt'], margin_outer=active_margin,
            truss_fillet=p['truss_fillet'], min_hole_dia=p['min_hole_dia'], xb_t_list=xb_t_list, x_dia=x_dia,
            plank_start=p['plank_start'], plank_end=p['plank_end'],
            plank_part_start=p.get('plank_part_start', p['plank_start']),
            plank_part_end=p.get('plank_part_end', p['plank_end']),
            plank_thick=p['plank_thick'], stringers_data=p['stringers_data'], te_cut=te_cut_val,
            apply_safe_margin=p['safe_margin_var'],
            te_cap_uf_act=p['te_cap_uf_act'], te_cap_uf_w=p['te_cap_uf_w'],
            te_cap_ur_act=p['te_cap_ur_act'], te_cap_ur_w=p['te_cap_ur_w'],
            te_cap_lf_act=p['te_cap_lf_act'], te_cap_lf_w=p['te_cap_lf_w'],
            te_cap_lr_act=p['te_cap_lr_act'], te_cap_lr_w=p['te_cap_lr_w'],
            te_cap_thick=p['te_cap_thick'],
            rc1_act=p['rc1_act'], rc1_start=p['rc1_start'], rc1_end=p['rc1_end'], rc1_thick=p['rc1_thick'],
            rc2_act=p['rc2_act'], rc2_start=p['rc2_start'], rc2_end=p['rc2_end'], rc2_thick=p['rc2_thick'],
            bolt1_dx=b1[0], bolt1_dy=b1[1], bolt1_dia=b1[2],
            bolt2_dx=b2[0], bolt2_dy=b2[1], bolt2_dia=b2[2],
            diag_params_list=diag_params, fast_mode=p.get('fast_mode', False),
            tabs_active=p.get('tabs_active', True),
            truss_tab_width=float(p.get('truss_tab_width', '4.0')),
            le_interp_active=p.get('le_interp_active', False),
            le_interp_range=p.get('le_interp_range', 10.0),
            le_interp_divisions=int(p.get('le_interp_divisions', 50))
        )
        
        return self.generate_single_rib(params_obj)

    def export_dxf(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None, jig_pts=None, doc=None, msp=None, offset=(0,0), layer_flags=None):
        if ezdxf is None: raise ImportError("ezdxf is required.")
        if layer_flags is None:
            layer_flags = {}

        save_required = False
        if doc is None or msp is None:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            save_required = True

        try:
            doc.layers.add(name='RIB_OUTLINE', color=7)
            doc.layers.add(name='HOLES', color=1)
            doc.layers.add(name='TRUSS', color=2)
            doc.layers.add(name='PLANK', color=3)
            doc.layers.add(name='TE_PART', color=4)
            doc.layers.add(name='JIG_OUTLINE', color=5)
            doc.layers.add(name='TE_CAPS', color=6)
            doc.layers.add(name='RIB_CAPS', color=5)
        except Exception:
            try:
                doc.layers.new(name='RIB_OUTLINE', dxfattribs={'color': 7})
                doc.layers.new(name='HOLES', dxfattribs={'color': 1})
                doc.layers.new(name='TRUSS', dxfattribs={'color': 2})
                doc.layers.new(name='PLANK', dxfattribs={'color': 3})
                doc.layers.new(name='TE_PART', dxfattribs={'color': 4})
                doc.layers.new(name='JIG_OUTLINE', dxfattribs={'color': 5})
                doc.layers.new(name='TE_CAPS', dxfattribs={'color': 6})
                doc.layers.new(name='RIB_CAPS', dxfattribs={'color': 5})
            except Exception:
                pass

        origin_pt = np.array(origin)
        def shift(p): return (float(p[0] - origin_pt[0] + offset[0]), float(p[1] - origin_pt[1] + offset[1]))
        def shift_poly(poly): return [(float(pt[0] - origin_pt[0] + offset[0]), float(pt[1] - origin_pt[1] + offset[1])) for pt in poly]
        
        if layer_flags.get('dxf_layer_rib_outline', True):
            if len(rib_pts) > 0: msp.add_lwpolyline(shift_poly(rib_pts), close=True, dxfattribs={'layer': 'RIB_OUTLINE'})
        
        if layer_flags.get('dxf_layer_holes', True):
            if d_m >= 0: msp.add_circle(center=shift(c_m), radius=d_m/2.0, dxfattribs={'layer': 'HOLES'})
            if d_f >= 0: msp.add_circle(center=shift(c_f), radius=d_f/2.0, dxfattribs={'layer': 'HOLES'})
            if d_r >= 0: msp.add_circle(center=shift(c_r), radius=d_r/2.0, dxfattribs={'layer': 'HOLES'})
            if d_b1 >= 0: msp.add_circle(center=shift(c_b1), radius=d_b1/2.0, dxfattribs={'layer': 'HOLES'})
            if d_b2 >= 0: msp.add_circle(center=shift(c_b2), radius=d_b2/2.0, dxfattribs={'layer': 'HOLES'})
            for diag_poly_pts in diag_poly_pts_list:
                if len(diag_poly_pts) > 0: msp.add_lwpolyline(shift_poly(diag_poly_pts), close=True, dxfattribs={'layer': 'HOLES'})

        if layer_flags.get('dxf_layer_truss', True):
            for c in xb_centers: msp.add_circle(center=shift(c), radius=d_xb/2.0, dxfattribs={'layer': 'TRUSS'})
            for h in truss_holes: msp.add_lwpolyline(shift_poly(h), close=True, dxfattribs={'layer': 'TRUSS'})

        if layer_flags.get('dxf_layer_plank', True):
            if len(plank_poly) > 0: msp.add_lwpolyline(shift_poly(plank_poly), close=True, dxfattribs={'layer': 'PLANK'})

        if layer_flags.get('dxf_layer_te_part', True):
            if len(te_part) > 0: msp.add_lwpolyline(shift_poly(te_part), close=True, dxfattribs={'layer': 'TE_PART'})
            if te_cap_pts_list is not None:
                for cap_pts in te_cap_pts_list:
                    if len(cap_pts) > 0: msp.add_lwpolyline(shift_poly(cap_pts), close=True, dxfattribs={'layer': 'TE_CAPS'})
            if rc_cap_pts_list is not None:
                for cap_pts in rc_cap_pts_list[0] + rc_cap_pts_list[1]:
                    if len(cap_pts) > 0: msp.add_lwpolyline(shift_poly(cap_pts), close=True, dxfattribs={'layer': 'RIB_CAPS'})

        if layer_flags.get('dxf_layer_jig_outline', True):
            if jig_pts is not None and len(jig_pts) > 0: msp.add_lwpolyline(shift_poly(jig_pts), close=True, dxfattribs={'layer': 'JIG_OUTLINE'})

        if save_required:
            doc.saveas(filepath)

    def export_single_poly_dxf(self, filepath, poly_pts, origin, doc=None, msp=None, offset=(0,0)):
        if ezdxf is None: raise ImportError("ezdxf is required.")
        
        save_required = False
        if doc is None or msp is None:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            save_required = True

        try:
            doc.layers.add(name='OUTLINE', color=7)
        except Exception:
            try:
                doc.layers.new(name='OUTLINE', dxfattribs={'color': 7})
            except Exception:
                pass

        pts = []
        for p in poly_pts:
            pts.append((p[0] - origin[0] + offset[0], p[1] - origin[1] + offset[1]))
            
        if len(pts) > 0:
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'OUTLINE'})
            
        doc.saveas(filepath)
        
    def generate_jig_at_y(self, p, y_local: float, return_full=False):
        import numpy as np
        from shapely.geometry import Polygon, box, Point, LineString
        from shapely.ops import unary_union
        
        chord, spar_pct, washout, t, xb_t_list, x_dia = self.get_local_params(p, y_local)
        
        te_cut = p.get('te_cut', 0.0)
        d_m = p.get('spar_hole_dia', 0.0)
        dv_m = p.get('spar_hole_dv', 0.0)
        d_r = p.get('rear_spar_dia', 0.0)
        d_f = p.get('front_spar_dia', 0.0)
        
        front_dx_root = p.get('front_spar_dx_root', p.get('front_spar_dx', 0.0))
        front_dx_tip = p.get('front_spar_dx_tip', p.get('front_spar_dx', 0.0))
        front_dy_root = p.get('front_spar_dy_root', p.get('front_spar_dy', 0.0))
        front_dy_tip = p.get('front_spar_dy_tip', p.get('front_spar_dy', 0.0))
        front_dx = front_dx_root * (1 - t) + front_dx_tip * t
        front_dy = front_dy_root * (1 - t) + front_dy_tip * t

        rear_dx_root = p.get('rear_spar_dx_root', p.get('rear_spar_dx', 0.0))
        rear_dx_tip = p.get('rear_spar_dx_tip', p.get('rear_spar_dx', 0.0))
        rear_dy_root = p.get('rear_spar_dy_root', p.get('rear_spar_dy', 0.0))
        rear_dy_tip = p.get('rear_spar_dy_tip', p.get('rear_spar_dy', 0.0))
        rear_dx = rear_dx_root * (1 - t) + rear_dx_tip * t
        rear_dy = rear_dy_root * (1 - t) + rear_dy_tip * t
        
        try:
            pts1 = self.load_dat(p.get('file1', ''))
            pts2 = self.load_dat(p.get('file2', ''))
            if len(pts1) == 0 or len(pts2) == 0:
                print(f"Jig generation error at Y={y_local}: Missing valid dat files")
                return None
                
            n_pts = 300
            blended = self.resample_airfoil(pts1, n_pts) * (1.0 - t) + self.resample_airfoil(pts2, n_pts) * t
            scaled = blended * chord
            
            le_idx = np.argmin(scaled[:, 0])
            u_x_orig, u_y_orig = scaled[:le_idx+1, 0][::-1], scaled[:le_idx+1, 1][::-1]
            l_x_orig, l_y_orig = scaled[le_idx:, 0], scaled[le_idx:, 1]

            spar_x = chord * (spar_pct / 100.0)
            spar_y_pre = (np.interp(spar_x, u_x_orig, u_y_orig) + np.interp(spar_x, l_x_orig, l_y_orig)) / 2.0

            w_theta = np.radians(washout)
            R_mat = np.array([[np.cos(w_theta), -np.sin(w_theta)], [np.sin(w_theta), np.cos(w_theta)]])

            rotated = (scaled - [spar_x, spar_y_pre]).dot(R_mat.T) + [spar_x, spar_y_pre]

            le_idx = np.argmin(rotated[:, 0])
            u_x, u_y = rotated[:le_idx+1, 0][::-1], rotated[:le_idx+1, 1][::-1]
            l_x, l_y = rotated[le_idx:, 0], rotated[le_idx:, 1]
            
            c_m = np.array([spar_x, spar_y_pre])
            c_r = (np.array([spar_x + rear_dx, spar_y_pre + rear_dy]) - c_m).dot(R_mat.T) + c_m
            c_f = (np.array([spar_x + front_dx, spar_y_pre + front_dy]) - c_m).dot(R_mat.T) + c_m
            
        except Exception as e:
            print(f"Jig generation error at Y={y_local}: {e}")
            return None

        # Early calculation of TE coordinates
        te_pad_width = te_cut + 10.0
        unrot_end_x = chord
        unrot_start_x = chord - te_pad_width
        
        pad_x_orig = []
        pad_y_orig = []
        sort_idx = np.argsort(l_x_orig)
        l_x_sorted = np.array(l_x_orig)[sort_idx]
        l_y_sorted = np.array(l_y_orig)[sort_idx]
        
        pad_x_orig.append(unrot_start_x)
        pad_y_orig.append(np.interp(unrot_start_x, l_x_sorted, l_y_sorted))
        for xi, yi in zip(l_x_sorted, l_y_sorted):
            if unrot_start_x < xi < unrot_end_x:
                pad_x_orig.append(xi)
                pad_y_orig.append(yi)
        pad_x_orig.append(unrot_end_x)
        pad_y_orig.append(np.interp(unrot_end_x, l_x_sorted, l_y_sorted))
        
        pad_pts_orig = np.column_stack((pad_x_orig, pad_y_orig))
        rotated_pad_pts = (pad_pts_orig - [spar_x, spar_y_pre]).dot(R_mat.T) + [spar_x, spar_y_pre]
        
        te_x_arr = rotated_pad_pts[:, 0]
        te_y_arr = rotated_pad_pts[:, 1]
        
        # Calculate Base Y
        base_height = float(p.get('jig_base_height', 100.0))
        base_y = c_m[1] - base_height
        jig_wall_thickness = float(p.get('jig_wall_thickness', 10.0))
        
        # Calculate Stopper End X
        stopper_height = float(p.get('jig_te_stopper_height', 10.0))
        if stopper_height > 0:
            stopper_back_x = te_x_arr[-1] + jig_wall_thickness
        else:
            stopper_back_x = te_x_arr[-1]
            
        # Calculate Slot Centers based on the smallest rib's chordwise midpoint
        chord_root = float(p.get('chord_root', 200.0))
        chord_tip = float(p.get('chord_tip', 200.0))
        if chord_tip <= chord_root:
            min_chord = chord_tip
            spar_pos_min = float(p.get('spar_pos_tip', 30.0))
        else:
            min_chord = chord_root
            spar_pos_min = float(p.get('spar_pos_root', 30.0))
            
        spar_x_min = min_chord * spar_pos_min / 100.0
        slot_center_from_le_min = min_chord / 2.0
        slot_offset_from_spar = slot_center_from_le_min - spar_x_min
        
        slot_center_x = c_m[0] + slot_offset_from_spar
        
        slot_interval = float(p.get('jig_slot_interval', 100.0))
        slot_width = float(p.get('jig_slot_width', 3.0))
        slot_depth = float(p.get('jig_slot_depth', 10.0))
        slot1_x = slot_center_x - slot_interval / 2.0
        slot2_x = slot_center_x + slot_interval / 2.0
        
        # Define base limits
        front_pillar_left = (c_f[0] - d_f/2.0) - jig_wall_thickness if d_f >= 0 else (c_m[0] - d_m/2.0) - jig_wall_thickness
        slot1_left = slot1_x - slot_width / 2.0
        base_start_x = min(front_pillar_left, slot1_left - jig_wall_thickness)

        # User constraint: jig ends at trailing edge support, unless slot2 extends further
        slot2_right = slot2_x + slot_width / 2.0
        base_end_x = max(stopper_back_x, slot2_right + jig_wall_thickness)
        
        # Create base poly
        base_thickness = float(p.get('jig_base_thickness', 25.0))
        base_poly = box(base_start_x, base_y, base_end_x, base_y + base_thickness)
        
        angle_deg = float(p.get('jig_pillar_angle', 90.0))
        clearances = []
        
        # Helper to create a trapezoidal pillar for a spar
        def create_pillar(c, d, dv=None):
            if dv is None or dv <= 0: dv = d
            box_w = d + 2.0 * jig_wall_thickness
            box_top_y = c[1] + dv * 0.1
            
            box_left = c[0] - box_w / 2.0
            box_right = c[0] + box_w / 2.0
            
            # Pillar polygon
            dy_down = box_top_y - (base_y + base_thickness)
            if angle_deg < 90.0 and dy_down > 0:
                dx_down = dy_down / np.tan(np.radians(angle_deg))
            else:
                dx_down = 0.0
                
            pillar_pts = [
                (box_left, box_top_y),
                (box_right, box_top_y),
                (box_right + dx_down, base_y + base_thickness),
                (box_right + dx_down, base_y),
                (box_left - dx_down, base_y),
                (box_left - dx_down, base_y + base_thickness),
            ]
            
            # Clearance polygon to subtract from thick base_poly
            y_top = base_y + max(base_thickness, 1000.0)
            dy_up = y_top - box_top_y
            if angle_deg < 90.0 and dy_up > 0:
                dx_up = dy_up / np.tan(np.radians(angle_deg))
            else:
                dx_up = 0.0
                
            clearance_pts = [
                (box_left - dx_up, y_top),
                (box_left, box_top_y),
                (box_right, box_top_y),
                (box_right + dx_up, y_top),
                (box_right + dx_up, y_top + 1000.0),
                (box_left - dx_up, y_top + 1000.0)
            ]
            clearances.append(Polygon(clearance_pts))
            
            return Polygon(pillar_pts)
        
        # Create Solid Pillars
        pillars = []
        if d_f >= 0: pillars.append(create_pillar(c_f, d_f))
        if d_m >= 0: pillars.append(create_pillar(c_m, d_m, dv_m))
        if d_r >= 0: pillars.append(create_pillar(c_r, d_r))
        
        frame = unary_union(pillars) if pillars else Polygon()
        
        if len(te_x_arr) >= 2:
            # TE solid block from base up to the tracing curve
            te_block_pts = [(te_x_arr[0], base_y)]
            te_block_pts.extend(list(zip(te_x_arr, te_y_arr)))
            te_block_pts.append((te_x_arr[-1], base_y))
            te_block_pts.append((te_x_arr[0], base_y)) # Close
            te_block = Polygon(te_block_pts).buffer(0)
            frame = frame.union(te_block)
            
            # Add TE Stopper wall
            if stopper_height > 0:
                stopper_front_x = te_x_arr[-1]
                stopper_top_y = te_y_arr[-1] + stopper_height
                stopper_poly = box(stopper_front_x, base_y, stopper_back_x, stopper_top_y)
                frame = frame.union(stopper_poly)
                
            # TE Clearance logic to prevent thick base bar from burying TE support
            y_top = base_y + max(base_thickness, 1000.0)
            dy_up_te = y_top - te_y_arr[0]
            if angle_deg < 90.0 and dy_up_te > 0:
                dx_up_te = dy_up_te / np.tan(np.radians(angle_deg))
            else:
                dx_up_te = 0.0
                
            te_clearance_pts = [(te_x_arr[0] - dx_up_te, y_top), (te_x_arr[0], te_y_arr[0])]
            te_clearance_pts.extend(list(zip(te_x_arr, te_y_arr)))
            
            if stopper_height > 0:
                dy_up_stopper = y_top - stopper_top_y
                if angle_deg < 90.0 and dy_up_stopper > 0:
                    dx_up_stopper = dy_up_stopper / np.tan(np.radians(angle_deg))
                else:
                    dx_up_stopper = 0.0
                
                te_clearance_pts.append((stopper_front_x, stopper_top_y))
                te_clearance_pts.append((stopper_back_x, stopper_top_y))
                te_clearance_pts.append((stopper_back_x + dx_up_stopper, y_top))
            else:
                dy_up_te_right = y_top - te_y_arr[-1]
                if angle_deg < 90.0 and dy_up_te_right > 0:
                    dx_up_te_right = dy_up_te_right / np.tan(np.radians(angle_deg))
                else:
                    dx_up_te_right = 0.0
                te_clearance_pts.append((te_x_arr[-1] + dx_up_te_right, y_top))
                
            te_clearance_pts.append((te_x_arr[0] - dx_up_te, y_top)) # close
            te_clearance_poly = Polygon(te_clearance_pts).buffer(0)
            clearances.append(te_clearance_poly)
            
        # Now that ALL clearances (pillars + TE) are collected, process the base
        if clearances:
            base_poly = base_poly.difference(unary_union(clearances))
            
        # Union with solid base
        frame = frame.union(base_poly)
            
        # Cut spar holes (Rectangular boxes, width d, bottom at c_y - d/2)
        if d_f >= 0:
            f_cut = box(c_f[0] - d_f/2.0, c_f[1] - d_f/2.0, c_f[0] + d_f/2.0, c_f[1] + d_f)
            frame = frame.difference(f_cut)
            
        if d_m >= 0:
            dv = dv_m if dv_m >= 0 else d_m
            m_cut = box(c_m[0] - d_m/2.0, c_m[1] - dv/2.0, c_m[0] + d_m/2.0, c_m[1] + dv)
            frame = frame.difference(m_cut)
            
        if d_r >= 0:
            r_cut = box(c_r[0] - d_r/2.0, c_r[1] - d_r/2.0, c_r[0] + d_r/2.0, c_r[1] + d_r)
            frame = frame.difference(r_cut)
            
        # Slots on the base plate
        s1 = box(slot1_x - slot_width/2.0, base_y - 1.0, slot1_x + slot_width/2.0, base_y + slot_depth)
        s2 = box(slot2_x - slot_width/2.0, base_y - 1.0, slot2_x + slot_width/2.0, base_y + slot_depth)
        frame = frame.difference(s1.union(s2))

        # Extract polygon coordinates
        jig_pts = None
        if getattr(frame, 'geom_type', '') == 'Polygon':
            jig_pts = list(frame.exterior.coords)
        elif getattr(frame, 'geom_type', '') == 'MultiPolygon':
            largest = max(frame.geoms, key=lambda a: a.area)
            jig_pts = list(largest.exterior.coords)
        elif getattr(frame, 'geom_type', '') == 'GeometryCollection':
            polys = [g for g in frame.geoms if getattr(g, 'geom_type', '') == 'Polygon']
            if polys:
                largest = max(polys, key=lambda a: a.area)
                jig_pts = list(largest.exterior.coords)
            
        if return_full:
            return {
                'jig_pts': jig_pts,
                'wing_pts': rotated.tolist(),
                'c_m': c_m.tolist(),
                'd_m': d_m,
                'dv_m': dv_m,
                'c_f': c_f.tolist(),
                'd_f': d_f,
                'c_r': c_r.tolist(),
                'd_r': d_r
            }
        return jig_pts
