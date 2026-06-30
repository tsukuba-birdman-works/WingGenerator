import os
import numpy as np

try:
    import trimesh
    from shapely.geometry import Polygon
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False

class WingtipFinEngine:
    def __init__(self):
        pass

    def load_dat(self, filepath):
        pts = []
        if not filepath or not os.path.exists(filepath):
            return np.array([])
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

    def resample_airfoil(self, points, target_count=100):
        if len(points) == 0:
            return points
        # linear interpolation along cumulative contour length
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
        distances = np.insert(distances, 0, 0)
        target_distances = np.linspace(0, distances[-1], target_count)
        x_interp = np.interp(target_distances, distances, points[:, 0])
        y_interp = np.interp(target_distances, distances, points[:, 1])
        return np.column_stack((x_interp, y_interp))

    def get_interpolated_airfoil_coords(self, pts_up_rev, pts_low, N_points_half):
        airfoil_x = np.linspace(0, 1, N_points_half)
        airfoil_z_up = np.interp(airfoil_x, pts_up_rev[:, 0], pts_up_rev[:, 1])
        airfoil_z_low = np.interp(airfoil_x, pts_low[:, 0], pts_low[:, 1])
        return airfoil_x, airfoil_z_up, airfoil_z_low

    def generate_fin_mesh(self, params):
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh and shapely are required for 3D export.")

        # Parse parameters
        airfoil_path = params.get('airfoil_path', '')
        span = float(params.get('span', 250.0))
        cant_angle = float(params.get('cant_angle', 45.0))
        sweep_angle = float(params.get('sweep_angle', 30.0))
        taper_ratio = float(params.get('taper_ratio', 0.1))
        twist_deg = float(params.get('twist_deg', -2.0))
        thickness_scale = float(params.get('thickness_scale', 1.0))
        chord_root = float(params.get('chord_root', 200.0))
        spar_pct = float(params.get('spar_pct', 40.0))
        style = params.get('style', 'Horner Upward')
        color_rgba = params.get('color_rgba', [135, 206, 235, 255])
        hoerner_power = float(params.get('hoerner_power', 2.0))
        curve_power = max(1.05, float(params.get('curve_power', 2.0)))
        y_slices = int(params.get('y_slices', 20))

        winglet_w_flat = float(params.get('winglet_w_flat', 50.0))
        winglet_r_bend = float(params.get('winglet_r_bend', 50.0))
        winglet_h_up = float(params.get('winglet_h_up', 150.0))

        # Main Wing Parameters for C1 continuity and spar path
        main_span = float(params.get('main_span', 500.0))
        main_chord_root = float(params.get('main_chord_root', 300.0))
        main_sweep = float(params.get('main_sweep', 15.0))
        main_spar_pct_root = float(params.get('main_spar_pct_root', 40.0))
        main_spar_pct_tip = float(params.get('main_spar_pct_tip', 40.0))
        
        wing_side = params.get('wing_side', 'Right')
        S_side = -1.0 if wing_side == "Left" else 1.0
        X_spar_root = chord_root * (main_spar_pct_tip / 100.0)

        # Load airfoil
        raw_pts = self.load_dat(airfoil_path)
        if len(raw_pts) < 3:
            x = np.linspace(0, 1, 50)
            y = 0.12 * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
            pts_up = np.column_stack((x[::-1], y[::-1]))
            pts_down = np.column_stack((x[1:], -y[1:]))
            raw_pts = np.vstack((pts_up, pts_down))

        le_idx = np.argmin(raw_pts[:, 0])
        pts_up_rev = raw_pts[:le_idx+1][::-1]
        pts_low = raw_pts[le_idx:]
        
        N_points_half = 50
        airfoil_x, airfoil_z_up, airfoil_z_low = self.get_interpolated_airfoil_coords(pts_up_rev, pts_low, N_points_half)

        # C1-continuous coefficients
        s_0 = np.tan(np.radians(main_sweep))
        s_1 = np.tan(np.radians(sweep_angle))
        
        # Chord slope at root (from main wing taper rate)
        c_prime_0 = (chord_root - main_chord_root) / main_span
        chord_tip = chord_root * taper_ratio
        
        # Chord coefficient D using general power curve_power
        if style == "Winglet":
            theta = np.radians(cant_angle)
            S_bend = winglet_r_bend * theta
            S_total = winglet_w_flat + S_bend + winglet_h_up
            effective_span = S_total
            Y_end2 = winglet_w_flat + winglet_r_bend * np.sin(theta)
            Z_end2 = winglet_r_bend * (1.0 - np.cos(theta))
        else:
            effective_span = span
            S_total = span

        D = (chord_tip - chord_root - c_prime_0 * effective_span) / (effective_span**curve_power)

        tip_points_up = []
        tip_points_low = []
        spar_line = []

        for i in range(y_slices + 1):
            t = i / y_slices
            y_real = t * effective_span
            
            # C1-continuous Chord and Sweep calculations
            if "Horner" in style:
                C_t = max(2.0, D * (y_real**curve_power) + c_prime_0 * y_real + chord_root)
                X_LE = ((s_1 - s_0) / (span**(curve_power - 1.0))) * (y_real**curve_power) + s_0 * y_real
            elif style == "Winglet":
                # Centerline coordinates (Y, Z) and rotation angle phi
                if y_real <= winglet_w_flat:
                    y_mid = y_real
                    z_mid = 0.0
                    phi = 0.0
                elif y_real <= (winglet_w_flat + S_bend):
                    ds = y_real - winglet_w_flat
                    phi = ds / winglet_r_bend
                    y_mid = winglet_w_flat + winglet_r_bend * np.sin(phi)
                    z_mid = winglet_r_bend * (1.0 - np.cos(phi))
                else:
                    ds = y_real - (winglet_w_flat + S_bend)
                    phi = theta
                    y_mid = Y_end2 + ds * np.cos(theta)
                    z_mid = Z_end2 + ds * np.sin(theta)
                
                C_t = max(2.0, D * (y_real**curve_power) + c_prime_0 * y_real + chord_root)
                X_LE = ((s_1 - s_0) / (effective_span**(curve_power - 1.0))) * (y_real**curve_power) + s_0 * y_real
            elif style == "Round Dome":
                f_t = np.sqrt(max(0.0, 1.0 - t**2))
                C_t = max(2.0, chord_root * f_t)
                X_LE = X_spar_root - (chord_root * (main_spar_pct_tip / 100.0)) * f_t + s_0 * y_real
            else:
                # Flat/Standard uses standard linear definitions
                C_t = chord_root * (1.0 - t * (1.0 - taper_ratio))
                X_LE = y_real * np.tan(np.radians(sweep_angle))
            
            x_real = X_LE + (airfoil_x * C_t)
            
            # C1-continuous spar percentage interpolation
            if main_span > 0:
                k_spar = (main_spar_pct_tip - main_spar_pct_root) / main_span
            else:
                k_spar = 0.0
            F_spar = k_spar * effective_span
            G_spar = main_spar_pct_tip
            E_spar = spar_pct - G_spar - F_spar
            
            spar_pct_t = E_spar * (t**2) + F_spar * t + G_spar
            
            # Record 3D spar line point
            spar_x_local = C_t * (spar_pct_t / 100.0)
            cant_rad = np.radians(cant_angle)
            X_spar = spar_x_local + X_LE
            
            # For Horner style and Round Dome, Y is flat and Z has no cant angle offset (Z_center = 0)
            if style == "Winglet":
                Y_spar = y_mid
                Z_spar = z_mid
            elif "Horner" in style or style == "Round Dome":
                Y_spar = y_real
                Z_spar = 0.0
            else:
                Y_spar = y_real * np.cos(cant_rad)
                Z_spar = y_real * np.sin(cant_rad)
                
            spar_line.append([X_spar - X_spar_root, Y_spar * S_side, Z_spar])
            
            if "Horner" in style:
                thickness = (airfoil_z_up - airfoil_z_low) * C_t
                if style == "Horner Downward":
                    z_low_real = airfoil_z_low * C_t
                    z_up_real = z_low_real + thickness * (1.0 - (t**hoerner_power))
                elif style == "Horner Upward":
                    z_up_real = airfoil_z_up * C_t
                    z_low_real = z_up_real - thickness * (1.0 - (t**hoerner_power))
                else: # Symmetrical
                    z_mean = (airfoil_z_up + airfoil_z_low) / 2.0 * C_t
                    thickness_t = thickness * (1.0 - (t**hoerner_power))
                    z_up_real = z_mean + thickness_t / 2.0
                    z_low_real = z_mean - thickness_t / 2.0
                
                pts_u = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_up_real))
                pts_l = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_low_real))
            elif style == "Round Dome":
                z_up_real = airfoil_z_up * C_t * thickness_scale
                z_low_real = airfoil_z_low * C_t * thickness_scale
                
                pts_u = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_up_real))
                pts_l = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_low_real))
            elif style == "Winglet":
                twist_y = t * twist_deg
                twist_rad = np.radians(twist_y)
                cos_t, sin_t = np.cos(twist_rad), np.sin(twist_rad)
                
                x_rel_up = (airfoil_x * C_t) - spar_x_local
                z_rel_up = airfoil_z_up * C_t * thickness_scale
                x_rot_up = x_rel_up * cos_t - z_rel_up * sin_t
                z_rot_up = x_rel_up * sin_t + z_rel_up * cos_t
                
                X_up = spar_x_local + x_rot_up + X_LE
                Y_up = y_mid - z_rot_up * np.sin(phi)
                Z_up = z_mid + z_rot_up * np.cos(phi)
                
                x_rel_low = (airfoil_x * C_t) - spar_x_local
                z_rel_low = airfoil_z_low * C_t * thickness_scale
                x_rot_low = x_rel_low * cos_t - z_rel_low * sin_t
                z_rot_low = x_rel_low * sin_t + z_rel_low * cos_t
                
                X_low = spar_x_local + x_rot_low + X_LE
                Y_low = y_mid - z_rot_low * np.sin(phi)
                Z_low = z_mid + z_rot_low * np.cos(phi)
                
                pts_u = np.column_stack((X_up - X_spar_root, Y_up * S_side, Z_up))
                pts_l = np.column_stack((X_low - X_spar_root, Y_low * S_side, Z_low))
            else:
                # Flat / Standard
                twist_y = t * twist_deg
                twist_rad = np.radians(twist_y)
                cos_t, sin_t = np.cos(twist_rad), np.sin(twist_rad)
                
                x_rel_up = (airfoil_x * C_t) - spar_x_local
                z_rel_up = airfoil_z_up * C_t * thickness_scale
                x_rot_up = x_rel_up * cos_t - z_rel_up * sin_t
                z_rot_up = x_rel_up * sin_t + z_rel_up * cos_t
                
                X_up = spar_x_local + x_rot_up + X_LE
                Y_up = y_real * np.cos(cant_rad) - z_rot_up * np.sin(cant_rad)
                Z_up = y_real * np.sin(cant_rad) + z_rot_up * np.cos(cant_rad)
                
                x_rel_low = (airfoil_x * C_t) - spar_x_local
                z_rel_low = airfoil_z_low * C_t * thickness_scale
                x_rot_low = x_rel_low * cos_t - z_rel_low * sin_t
                z_rot_low = x_rel_low * sin_t + z_rel_low * cos_t
                
                X_low = spar_x_local + x_rot_low + X_LE
                Y_low = y_real * np.cos(cant_rad) - z_rot_low * np.sin(cant_rad)
                Z_low = y_real * np.sin(cant_rad) + z_rot_low * np.cos(cant_rad)
                
                pts_u = np.column_stack((X_up - X_spar_root, Y_up * S_side, Z_up))
                pts_l = np.column_stack((X_low - X_spar_root, Y_low * S_side, Z_low))
                
            tip_points_up.append(pts_u)
            tip_points_low.append(pts_l)

        # Build Mesh
        N_points = N_points_half + N_points_half - 1
        vertices_grid = np.zeros((y_slices + 1, N_points, 3))
        
        for j in range(y_slices + 1):
            vertices_grid[j] = np.vstack((tip_points_up[j][::-1], tip_points_low[j][1:]))
            
        vertices = vertices_grid.reshape(-1, 3)
        faces = []
        
        # Skin faces
        for j in range(y_slices):
            for i in range(N_points):
                next_i = (i + 1) % N_points
                v0 = j * N_points + i
                v1 = j * N_points + next_i
                v2 = (j + 1) * N_points + next_i
                v3 = (j + 1) * N_points + i
                
                faces.append([v0, v1, v2])
                faces.append([v0, v2, v3])
                
        # Caps
        def add_cap(j, reverse_winding=False):
            t = j / y_slices
            y_real = t * effective_span
            if "Horner" in style:
                C_t = max(2.0, D * (y_real**curve_power) + c_prime_0 * y_real + chord_root)
                thickness = (airfoil_z_up - airfoil_z_low) * C_t
                if style == "Horner Downward":
                    z_l = airfoil_z_low * C_t
                    z_u = z_l + thickness * (1.0 - (t**hoerner_power))
                elif style == "Horner Upward":
                    z_u = airfoil_z_up * C_t
                    z_l = z_u - thickness * (1.0 - (t**hoerner_power))
                else:
                    z_mean = (airfoil_z_up + airfoil_z_low) / 2.0 * C_t
                    thickness_t = thickness * (1.0 - (t**hoerner_power))
                    z_u = z_mean + thickness_t / 2.0
                    z_l = z_mean - thickness_t / 2.0
            elif style == "Winglet":
                C_t = max(2.0, D * (y_real**curve_power) + c_prime_0 * y_real + chord_root)
                z_u = airfoil_z_up * C_t * thickness_scale
                z_l = airfoil_z_low * C_t * thickness_scale
            elif style == "Round Dome":
                f_t = np.sqrt(max(0.0, 1.0 - t**2))
                C_t = max(2.0, chord_root * f_t)
                z_u = airfoil_z_up * C_t * thickness_scale
                z_l = airfoil_z_low * C_t * thickness_scale
            else:
                C_t = chord_root * (1.0 - t * (1.0 - taper_ratio))
                z_u = airfoil_z_up * C_t * thickness_scale
                z_l = airfoil_z_low * C_t * thickness_scale
                
            x_2d = airfoil_x * C_t
            p2d_u = np.column_stack((x_2d, z_u))
            p2d_l = np.column_stack((x_2d, z_l))
            
            p2d = np.vstack((p2d_u[::-1], p2d_l[1:]))
            
            try:
                poly = Polygon(p2d).buffer(0)
                if not poly.is_empty and getattr(poly, 'geom_type', '') == 'Polygon':
                    cap_mesh = trimesh.creation.triangulate_polygon(poly)
                    idx_map = []
                    for v in cap_mesh[0]:
                        dists = np.sum((p2d - v)**2, axis=1)
                        idx_map.append(np.argmin(dists))
                    
                    offset = j * N_points
                    for f in cap_mesh[1]:
                        idx0 = offset + int(idx_map[f[0]])
                        idx1 = offset + int(idx_map[f[1]])
                        idx2 = offset + int(idx_map[f[2]])
                        if reverse_winding:
                            faces.append([idx0, idx2, idx1])
                        else:
                            faces.append([idx0, idx1, idx2])
            except Exception:
                offset = j * N_points
                for i in range(1, N_points - 1):
                    if reverse_winding:
                        faces.append([offset + 0, offset + i, offset + i + 1])
                    else:
                        faces.append([offset + 0, offset + i + 1, offset + i])
                        
        # Root cap (j = 0)
        add_cap(0, reverse_winding=True)
        
        # Tip cap (j = y_slices)
        if taper_ratio > 0.01 and "Horner" not in style and style != "Round Dome":
            add_cap(y_slices, reverse_winding=False)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        try:
            mesh.fix_normals()
        except:
            pass
            
        mesh.visual.face_colors = color_rgba
        try:
            from trimesh.visual.material import PBRMaterial
            mesh.visual.material = PBRMaterial(baseColorFactor=color_rgba, doubleSided=True)
        except:
            pass
            
        # Attach 3D spar line metadata
        mesh.metadata['spar_line'] = np.array(spar_line)
        return mesh

    def generate_main_wing_mesh(self, params):
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh and shapely are required.")

        # Parse parameters
        airfoil_path = params.get('airfoil_path', '')
        thickness_scale = float(params.get('thickness_scale', 1.0))
        chord_root = float(params.get('chord_root', 200.0))
        
        main_span = float(params.get('main_span', 500.0))
        main_chord_root = float(params.get('main_chord_root', 300.0))
        main_sweep = float(params.get('main_sweep', 15.0))
        main_airfoil_path = params.get('main_airfoil_path', '')
        
        # Spar position variables
        main_spar_pct_root = float(params.get('main_spar_pct_root', 40.0))
        main_spar_pct_tip = float(params.get('main_spar_pct_tip', 40.0))
        
        wing_side = params.get('wing_side', 'Right')
        S_side = -1.0 if wing_side == "Left" else 1.0
        X_spar_root = chord_root * (main_spar_pct_tip / 100.0)

        # Load root airfoil
        raw_pts_root = self.load_dat(main_airfoil_path)
        if len(raw_pts_root) < 3:
            raw_pts_root = self.load_dat(airfoil_path)
        if len(raw_pts_root) < 3:
            x = np.linspace(0, 1, 50)
            y = 0.12 * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
            pts_up = np.column_stack((x[::-1], y[::-1]))
            pts_down = np.column_stack((x[1:], -y[1:]))
            raw_pts_root = np.vstack((pts_up, pts_down))

        # Load tip airfoil (which is the fin root airfoil)
        raw_pts_tip = self.load_dat(airfoil_path)
        if len(raw_pts_tip) < 3:
            raw_pts_tip = raw_pts_root

        # Resample both
        N_points_half = 50
        
        le_idx_root = np.argmin(raw_pts_root[:, 0])
        pts_up_root = raw_pts_root[:le_idx_root+1][::-1]
        pts_low_root = raw_pts_root[le_idx_root:]
        _, z_up_root, z_low_root = self.get_interpolated_airfoil_coords(pts_up_root, pts_low_root, N_points_half)

        le_idx_tip = np.argmin(raw_pts_tip[:, 0])
        pts_up_tip = raw_pts_tip[:le_idx_tip+1][::-1]
        pts_low_tip = raw_pts_tip[le_idx_tip:]
        airfoil_x, z_up_tip, z_low_tip = self.get_interpolated_airfoil_coords(pts_up_tip, pts_low_tip, N_points_half)

        # Generate slices along main wing span (from y = -main_span to 0)
        N_main_slices = 15
        main_points_up = []
        main_points_low = []
        sweep_rad = np.radians(main_sweep)
        spar_line = []

        for j in range(N_main_slices + 1):
            t_main = j / N_main_slices
            y_real = -main_span * (1.0 - t_main)
            
            # Linear chord & sweep for the main wing
            C_t = main_chord_root + (chord_root - main_chord_root) * t_main
            X_LE = y_real * np.tan(sweep_rad)
            
            # Interpolated spar position
            spar_pct_y = main_spar_pct_root * (1.0 - t_main) + main_spar_pct_tip * t_main
            X_spar = X_LE + C_t * (spar_pct_y / 100.0)
            spar_line.append([X_spar - X_spar_root, y_real * S_side, 0.0])
            
            x_real = X_LE + (airfoil_x * C_t)
            
            # Interpolated airfoil coordinates
            z_u = z_up_root * (1.0 - t_main) + z_up_tip * t_main
            z_l = z_low_root * (1.0 - t_main) + z_low_tip * t_main
            
            z_up_real = z_u * C_t * thickness_scale
            z_low_real = z_l * C_t * thickness_scale
            
            pts_u = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_up_real))
            pts_l = np.column_stack((x_real - X_spar_root, np.full_like(x_real, y_real * S_side), z_low_real))
            
            main_points_up.append(pts_u)
            main_points_low.append(pts_l)

        # Build Mesh
        N_points = N_points_half + N_points_half - 1
        vertices_grid = np.zeros((N_main_slices + 1, N_points, 3))
        
        for j in range(N_main_slices + 1):
            vertices_grid[j] = np.vstack((main_points_up[j][::-1], main_points_low[j][1:]))
            
        vertices = vertices_grid.reshape(-1, 3)
        faces = []
        
        # Skin faces
        for j in range(N_main_slices):
            for i in range(N_points):
                next_i = (i + 1) % N_points
                v0 = j * N_points + i
                v1 = j * N_points + next_i
                v2 = (j + 1) * N_points + next_i
                v3 = (j + 1) * N_points + i
                
                faces.append([v0, v1, v2])
                faces.append([v0, v2, v3])
                
        # Root cap of the main wing (j = 0)
        def add_main_cap(j, reverse_winding=False):
            t_main = j / N_main_slices
            C_t = main_chord_root + (chord_root - main_chord_root) * t_main
            z_u = (z_up_root * (1.0 - t_main) + z_up_tip * t_main) * C_t * thickness_scale
            z_l = (z_low_root * (1.0 - t_main) + z_low_tip * t_main) * C_t * thickness_scale
            x_2d = airfoil_x * C_t
            p2d_u = np.column_stack((x_2d, z_u))
            p2d_l = np.column_stack((x_2d, z_l))
            p2d = np.vstack((p2d_u[::-1], p2d_l[1:]))
            try:
                poly = Polygon(p2d).buffer(0)
                if not poly.is_empty and getattr(poly, 'geom_type', '') == 'Polygon':
                    cap_mesh = trimesh.creation.triangulate_polygon(poly)
                    idx_map = []
                    for v in cap_mesh[0]:
                        dists = np.sum((p2d - v)**2, axis=1)
                        idx_map.append(np.argmin(dists))
                    offset = j * N_points
                    for f in cap_mesh[1]:
                        idx0 = offset + int(idx_map[f[0]])
                        idx1 = offset + int(idx_map[f[1]])
                        idx2 = offset + int(idx_map[f[2]])
                        if reverse_winding:
                            faces.append([idx0, idx2, idx1])
                        else:
                            faces.append([idx0, idx1, idx2])
            except Exception:
                offset = j * N_points
                for i in range(1, N_points - 1):
                    if reverse_winding:
                        faces.append([offset + 0, offset + i, offset + i + 1])
                    else:
                        faces.append([offset + 0, offset + i + 1, offset + i])

        add_main_cap(0, reverse_winding=True)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        try:
            mesh.fix_normals()
        except:
            pass
            
        mesh.visual.face_colors = [128, 128, 128, 100]
        try:
            from trimesh.visual.material import PBRMaterial
            mesh.visual.material = PBRMaterial(baseColorFactor=[128, 128, 128, 100], doubleSided=True, alphaMode='BLEND')
        except:
            pass
            
        # Attach 3D spar line metadata
        mesh.metadata['spar_line'] = np.array(spar_line)
        return mesh
