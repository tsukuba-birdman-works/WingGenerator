import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union, nearest_points
from typing import List, Dict, Any, Tuple

class SpindleCAMEngine:
    def __init__(self):
        pass

    def resample_path(self, path: List[Tuple[float, float]], spacing: float = 1.0) -> List[Tuple[float, float]]:
        """Resample path to ensure points are spaced no further than `spacing` mm apart."""
        if len(path) < 2:
            return path
        new_path = [path[0]]
        for i in range(len(path) - 1):
            p1 = np.array(path[i])
            p2 = np.array(path[i+1])
            d = p2 - p1
            dist = np.linalg.norm(d)
            if dist <= spacing:
                new_path.append(path[i+1])
            else:
                n_segments = int(np.ceil(dist / spacing))
                for j in range(1, n_segments + 1):
                    pt = p1 + d * (j / n_segments)
                    new_path.append((float(pt[0]), float(pt[1])))
        return new_path

    def get_z_at_point(self, x: float, y: float, tab_centers: List[Tuple[float, float]],
                       tab_width: float, cut_z: float, tab_z: float,
                       is_outer: bool, spar_x_coords: List[float], spar_y_shifted: float,
                       tab_angle_deg: float = 45.0) -> float:
        """Return the target Z height. If the tool is within the tab zone, lift towards tab_z using tab_angle_deg."""
        target_z = cut_z
        
        for tx, ty in tab_centers:
            dist = (x - tx)**2 + (y - ty)**2
            dist = dist ** 0.5
            w_half = tab_width / 2.0
            
            if dist <= w_half:
                # Flat top of the tab (the uncut material left)
                candidate_z = tab_z
                target_z = max(target_z, candidate_z)
            else:
                # Ramp down towards cut_z
                import math
                angle_rad = math.radians(tab_angle_deg)
                if angle_rad <= 0:
                    angle_rad = math.radians(90.0)
                    
                # Z decreases (goes deeper) as dist increases beyond w_half
                ramp_distance = dist - w_half
                ramp_z = tab_z - (ramp_distance * math.tan(angle_rad))
                
                # The Z cannot go deeper than cut_z
                candidate_z = max(cut_z, ramp_z)
                target_z = max(target_z, candidate_z)
                
        return min(target_z, tab_z) # Cap at tab_z (safety)

    def generate_gcode(self, rib_res, params: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Generate G-code for a single rib.
        Returns:
            gcode_string: The generated G-code program text.
            warnings: A list of any CAM-related warnings (e.g. tool too large for holes).
        """
        warnings = []
        gcode = []
        
        # 1. Parse CAM parameters
        tool_dia = float(params.get('cam_tool_dia', '2.0'))
        tool_radius = tool_dia / 2.0
        mat_thick = float(params.get('cam_mat_thick', '10.0'))
        safe_z = float(params.get('cam_safe_z', '5.0'))
        feed_rate = float(params.get('cam_feed_rate', '2000'))
        spindle_speed = float(params.get('cam_spindle_speed', '12000'))
        extra_depth = float(params.get('cam_extra_depth', '0.5'))
        tab_thickness = float(params.get('tab_thickness', '3.0'))
        tab_width = float(params.get('truss_tab_width', '4.0')) # default to truss tab width
        outer_tab_w = float(params.get('outer_tab_width', '6.0'))
        outer_tab_interval = float(params.get('outer_tab_interval', '100.0'))
        tab_angle_deg = float(params.get('tab_angle_deg', '45.0'))
        tabs_active = bool(params.get('tabs_active', True))
        milling_dir = str(params.get('cam_milling_dir', 'Conventional')).strip()
        
        cut_z = -(mat_thick + extra_depth)
        tab_z = -mat_thick + tab_thickness
        if tab_z > 0.0:
            tab_z = 0.0
            
        origin_pt = np.array(rib_res.c_m) # Shift relative to main spar center
        
        # Get elements from rib_res (index-safe fallback)
        rib_pts = rib_res.final_rib_mod
        final_truss_holes = rib_res.final_truss_holes
        diag_poly_pts_list = rib_res.diag_poly_pts_list
        
        # Determine spar parameters from UI/Config values
        d_m = float(params.get('spar_hole_dia', '0.0'))
        d_f = float(params.get('front_spar_dia', '0.0'))
        d_r = float(params.get('rear_spar_dia', '0.0'))
        
        d_b1 = float(params.get('bolt1_dia', '0.0'))
        d_b2 = float(params.get('bolt2_dia', '0.0'))
        d_xb = float(params.get('xbrace_dia', '0.0'))
        
        # Get tab centers from rib_res (index 24)
        raw_tab_centers = []
        if len(rib_res) > 24:
            raw_tab_centers = rib_res[24]
        
        # Shift tab centers to match G-code coordinates
        shifted_tab_centers = [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in raw_tab_centers]

        # Gather spar X coordinates (including diameter limits for main spar) for outer tab classification
        spar_x_coords = []
        if d_m > 0:
            r_m = d_m / 2.0
            spar_x_coords.extend([0.0, -r_m, r_m])
        if d_f > 0:
            c_f_shifted = rib_res.c_f - origin_pt
            spar_x_coords.append(float(c_f_shifted[0]))
        if d_r > 0:
            c_r_shifted = rib_res.c_r - origin_pt
            spar_x_coords.append(float(c_r_shifted[0]))

        # Toolpaths setup: (name, list of points, is_outer_contour, has_tabs)
        inner_toolpaths = []
        outer_toolpaths = []

        # Helper to shift a path
        def shift_path(pts):
            return [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in pts]

        # 2. Process Inner Holes
        # Main Spar Hole
        if d_m > 0:
            r_cut = (d_m / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"Main Spar Hole (dia {d_m}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(r_cut * np.cos(t), r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append(("Main Spar Hole", pts, False, False, None))

        # Front Spar Hole
        if d_f > 0:
            c_f_shifted = rib_res.c_f - origin_pt
            r_cut = (d_f / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"Front Spar Hole (dia {d_f}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(c_f_shifted[0] + r_cut * np.cos(t), c_f_shifted[1] + r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append(("Front Spar Hole", pts, False, False, None))

        # Rear Spar Hole
        if d_r > 0:
            c_r_shifted = rib_res.c_r - origin_pt
            r_cut = (d_r / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"Rear Spar Hole (dia {d_r}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(c_r_shifted[0] + r_cut * np.cos(t), c_r_shifted[1] + r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append(("Rear Spar Hole", pts, False, False, None))

        # Bolt 1 Hole
        if d_b1 > 0:
            c_b1_shifted = rib_res.c_b1 - origin_pt
            r_cut = (d_b1 / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"Bolt 1 Hole (dia {d_b1}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(c_b1_shifted[0] + r_cut * np.cos(t), c_b1_shifted[1] + r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append(("Bolt 1 Hole", pts, False, False, None))

        # Bolt 2 Hole
        if d_b2 > 0:
            c_b2_shifted = rib_res.c_b2 - origin_pt
            r_cut = (d_b2 / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"Bolt 2 Hole (dia {d_b2}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(c_b2_shifted[0] + r_cut * np.cos(t), c_b2_shifted[1] + r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append(("Bolt 2 Hole", pts, False, False, None))

        # Active X-Brace Holes
        for i, ct in enumerate(rib_res.active_xb_centers):
            c_xb_shifted = ct - origin_pt
            r_cut = (d_xb / 2.0) - tool_radius
            if r_cut <= 0.05:
                warnings.append(f"X-Brace Hole {i} (dia {d_xb}mm) is too small for tool (dia {tool_dia}mm)")
            else:
                pts = [(c_xb_shifted[0] + r_cut * np.cos(t), c_xb_shifted[1] + r_cut * np.sin(t)) for t in np.linspace(0, 2*np.pi, 64)]
                inner_toolpaths.append((f"X-Brace Hole {i}", pts, False, False, None))

        # Diagonal Spar Holes
        for i, diag_poly_pts in enumerate(diag_poly_pts_list):
            if len(diag_poly_pts) > 0:
                shifted = shift_path(diag_poly_pts)
                poly = Polygon(shifted)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                offset_poly = poly.buffer(-tool_radius, resolution=16)
                if offset_poly.is_empty:
                    warnings.append(f"Diagonal Spar Hole {i} is too narrow for tool (dia {tool_dia}mm)")
                else:
                    for g in (offset_poly.geoms if offset_poly.geom_type == 'MultiPolygon' else [offset_poly]):
                        inner_toolpaths.append((f"Diagonal Spar Hole {i}", list(g.exterior.coords), False, False, None))

        # Truss Holes (with tabs)
        for i, h in enumerate(final_truss_holes):
            if len(h) > 0:
                shifted = shift_path(h)
                poly = Polygon(shifted)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                offset_poly = poly.buffer(-tool_radius, resolution=16)
                if offset_poly.is_empty:
                    warnings.append(f"Truss Hole {i} is too narrow for tool (dia {tool_dia}mm)")
                else:
                    for g in (offset_poly.geoms if offset_poly.geom_type == 'MultiPolygon' else [offset_poly]):
                        inner_toolpaths.append((f"Truss Hole {i}", list(g.exterior.coords), False, True, None))

        # 3. Process Outer Contour with Spar Bridges

        
        poly_rib = None
        if len(rib_pts) > 0:
            shifted = shift_path(rib_pts)
            poly_rib = Polygon(shifted)
            if not poly_rib.is_valid:
                poly_rib = poly_rib.buffer(0)
                
        # Handle Spar Bridges
        spar_bridge_padding = float(params.get('spar_bridge_padding', '10.0'))
        spar_bridge_thickness = float(params.get('spar_bridge_thickness', '2.0'))
        bridge_z = -mat_thick + spar_bridge_thickness
        if bridge_z > 0: bridge_z = 0.0

        bridge_pocket_polys = []
        if poly_rib and poly_rib.is_valid:
            bridge_polys = []
            for c_shifted, d_spar in [(c_f_shifted if d_f > 0 else None, d_f), 
                                      (c_r_shifted if d_r > 0 else None, d_r)]:
                if c_shifted is not None and d_spar > 0:
                    pt_s = Point(c_shifted[0], c_shifted[1])
                    if not poly_rib.contains(pt_s):
                        pad_r = (d_spar / 2.0) + spar_bridge_padding
                        circle_s = pt_s.buffer(pad_r)
                        
                        p_near, _ = nearest_points(poly_rib.exterior, pt_s)
                        vx, vy = p_near.x - pt_s.x, p_near.y - pt_s.y
                        dist = np.hypot(vx, vy)
                        
                        if dist > 0:
                            ux, uy = vx / dist, vy / dist
                            nx, ny = -uy, ux
                            ext = 2.0
                            p1 = (pt_s.x + nx * pad_r, pt_s.y + ny * pad_r)
                            p2 = (pt_s.x - nx * pad_r, pt_s.y - ny * pad_r)
                            p3 = (p_near.x - nx * pad_r + ux * ext, p_near.y - ny * pad_r + uy * ext)
                            p4 = (p_near.x + nx * pad_r + ux * ext, p_near.y + ny * pad_r + uy * ext)
                            
                            bridge_rect = Polygon([p1, p2, p3, p4])
                            bridge_full = unary_union([circle_s, bridge_rect])
                            
                            bridge_polys.append(bridge_full)

            # --- Main Spar E-Shape Supports ---
            main_spar_support_w = float(params.get('main_spar_support_w', '2.0'))
            main_spar_support_h = float(params.get('main_spar_support_h', '5.0'))
            main_spar_support_thick = float(params.get('main_spar_support_thick', '2.0'))
            m_bridge_z = -mat_thick + main_spar_support_thick
            if m_bridge_z > 0: m_bridge_z = 0.0

            e_shape_polys = []
            if d_m > 0:
                w = main_spar_support_w
                h_bar = main_spar_support_h
                minx, miny, maxx, maxy = poly_rib.bounds
                
                shifted_stringers = []
                if hasattr(rib_res, 'stringer_pts_list') and rib_res.stringer_pts_list:
                    for st_pts in rib_res.stringer_pts_list:
                        s_pts = [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in st_pts]
                        shifted_stringers.append(Polygon(s_pts))
                        
                def find_clear_x(start_x, w, miny, maxy, stringer_polys, direction):
                    curr_x = start_x
                    while True:
                        leg_box = Polygon([
                            (curr_x - w/2, miny - 20), (curr_x + w/2, miny - 20),
                            (curr_x + w/2, maxy + 20), (curr_x - w/2, maxy + 20)
                        ])
                        min_dist = float('inf')
                        for sp in stringer_polys:
                            dist = leg_box.distance(sp)
                            if dist < min_dist:
                                min_dist = dist
                        if not stringer_polys or min_dist >= 2.0:
                            break
                        curr_x += direction * 0.5
                    return curr_x
                
                x_left = find_clear_x(-d_m/2.0, w, miny, maxy, shifted_stringers, -1)
                x_right = find_clear_x(d_m/2.0, w, miny, maxy, shifted_stringers, 1)
                x_coords = [x_left, 0.0, x_right]
                
                top_y_vals = []
                bot_y_vals = []
                for x in x_coords:
                    v_line = LineString([(x, miny - 10), (x, maxy + 10)])
                    inter = poly_rib.exterior.intersection(v_line)
                    if not inter.is_empty:
                        pts = []
                        if inter.geom_type == 'Point':
                            pts = [inter.y]
                        elif inter.geom_type in ['MultiPoint', 'GeometryCollection']:
                            pts = [p.y for p in inter.geoms if p.geom_type == 'Point']
                        if pts:
                            top_y_vals.append(max(pts))
                            bot_y_vals.append(min(pts))
                
                # Upper E-Shape (Tilted)
                if len(top_y_vals) == 3:
                    slope_l = (top_y_vals[1] - top_y_vals[0]) / (x_coords[1] - x_coords[0]) if x_coords[1] != x_coords[0] else 0.0
                    slope_r = (top_y_vals[2] - top_y_vals[1]) / (x_coords[2] - x_coords[1]) if x_coords[2] != x_coords[1] else 0.0
                    
                    left_x = x_coords[0] - w/2
                    left_y_bot = top_y_vals[0] + h_bar - (w/2)*slope_l
                    left_y_top = left_y_bot + w
                    
                    right_x = x_coords[-1] + w/2
                    right_y_bot = top_y_vals[2] + h_bar + (w/2)*slope_r
                    right_y_top = right_y_bot + w
                    
                    bar_poly = Polygon([
                        (left_x, left_y_bot), (x_coords[1], top_y_vals[1] + h_bar), (right_x, right_y_bot),
                        (right_x, right_y_top), (x_coords[1], top_y_vals[1] + h_bar + w), (left_x, left_y_top)
                    ])
                    
                    leg_polys = []
                    for x, y_rib in zip(x_coords, top_y_vals):
                        leg_polys.append(Polygon([
                            (x - w/2, y_rib - 2.0), (x + w/2, y_rib - 2.0),
                            (x + w/2, y_rib + h_bar + 0.1), (x - w/2, y_rib + h_bar + 0.1)
                        ]))
                    e_shape_polys.append(unary_union([bar_poly] + leg_polys))
                
                # Lower E-Shape (Tilted)
                if len(bot_y_vals) == 3:
                    slope_l = (bot_y_vals[1] - bot_y_vals[0]) / (x_coords[1] - x_coords[0]) if x_coords[1] != x_coords[0] else 0.0
                    slope_r = (bot_y_vals[2] - bot_y_vals[1]) / (x_coords[2] - x_coords[1]) if x_coords[2] != x_coords[1] else 0.0
                    
                    left_x = x_coords[0] - w/2
                    left_y_top = bot_y_vals[0] - h_bar - (w/2)*slope_l
                    left_y_bot = left_y_top - w
                    
                    right_x = x_coords[-1] + w/2
                    right_y_top = bot_y_vals[2] - h_bar + (w/2)*slope_r
                    right_y_bot = right_y_top - w
                    
                    bar_poly = Polygon([
                        (left_x, left_y_top), (x_coords[1], bot_y_vals[1] - h_bar), (right_x, right_y_top),
                        (right_x, right_y_bot), (x_coords[1], bot_y_vals[1] - h_bar - w), (left_x, left_y_bot)
                    ])
                    
                    leg_polys = []
                    for x, y_rib in zip(x_coords, bot_y_vals):
                        leg_polys.append(Polygon([
                            (x - w/2, y_rib - h_bar - 0.1), (x + w/2, y_rib - h_bar - 0.1),
                            (x + w/2, y_rib + 2.0), (x - w/2, y_rib + 2.0)
                        ]))
                    e_shape_polys.append(unary_union([bar_poly] + leg_polys))

            # Generate snap line toolpaths for Outer Spar Bridges
            original_offset_poly = poly_rib.buffer(tool_radius, resolution=16)
            if bridge_polys:
                for b_poly in bridge_polys:
                    snap_geom = original_offset_poly.exterior.intersection(b_poly.buffer(0.1))
                    if snap_geom.geom_type == 'LineString' and not snap_geom.is_empty:
                        inner_toolpaths.append(("Spar Bridge Snap Line", list(snap_geom.coords), False, False, bridge_z))
                    elif snap_geom.geom_type == 'MultiLineString':
                        for g in snap_geom.geoms:
                            if not g.is_empty:
                                inner_toolpaths.append(("Spar Bridge Snap Line", list(g.coords), False, False, bridge_z))

            # Generate snap line toolpaths for Main Spar E-Shapes
            if e_shape_polys:
                for e_poly in e_shape_polys:
                    snap_geom = original_offset_poly.exterior.intersection(e_poly.buffer(0.1))
                    if snap_geom.geom_type == 'LineString' and not snap_geom.is_empty:
                        inner_toolpaths.append(("Main Spar E-Support Snap", list(snap_geom.coords), False, False, m_bridge_z))
                    elif snap_geom.geom_type == 'MultiLineString':
                        for g in snap_geom.geoms:
                            if not g.is_empty:
                                inner_toolpaths.append(("Main Spar E-Support Snap", list(g.coords), False, False, m_bridge_z))

            all_support_polys = bridge_polys + e_shape_polys
            if all_support_polys:
                poly_rib = unary_union([poly_rib] + all_support_polys)
                if poly_rib.geom_type == 'MultiPolygon':
                    poly_rib = max(poly_rib.geoms, key=lambda p: p.area)
                    
            # Generate Outer Toolpath
            offset_poly = poly_rib.buffer(tool_radius, resolution=16)
            if offset_poly.is_empty:
                warnings.append("Rib Outer Contour offset failed (shape collapsed)")
            else:
                for g in (offset_poly.geoms if offset_poly.geom_type == 'MultiPolygon' else [offset_poly]):
                    for interior in g.interiors:
                        inner_toolpaths.append(("Support Gap Cutout", list(interior.coords), True, False, None))
                    outer_toolpaths.append(("Rib Outer Contour", list(g.exterior.coords), True, True, None))

        # 4. Generate G-code blocks
        gcode.append("; 3-Axis Spindle CNC Router G-Code Program")
        gcode.append(f"; Tool: Endmill {tool_dia}mm diameter")
        gcode.append(f"; Material Thickness: {mat_thick}mm (Styrofoam)")
        gcode.append(f"; Cut Feed: F{feed_rate:.1f}, Spindle Speed: S{spindle_speed:.0f}")
        gcode.append("G21 ; Units: Millimeters")
        gcode.append("G90 ; Coordinate system: Absolute")
        gcode.append(f"M3 S{spindle_speed:.0f} ; Spindle ON")
        gcode.append(f"G0 Z{safe_z:.3f} ; Raise tool to safe clearance height")

        # Sort inner toolpaths from Leading Edge to Trailing Edge (min X ascending)
        def get_min_x(path_tuple):
            path = path_tuple[1]
            if not path: return float('inf')
            return min(pt[0] for pt in path)
        inner_toolpaths.sort(key=get_min_x)

        # Rotate outer toolpaths to start from Trailing Edge (max X)
        for i in range(len(outer_toolpaths)):
            name, path, is_outer, has_tabs, spec_z = outer_toolpaths[i]
            if path and len(path) > 1:
                max_x_idx = max(range(len(path)-1), key=lambda idx: path[idx][0])
                if np.allclose(path[0], path[-1]):
                    path_core = path[:-1]
                else:
                    path_core = path
                rotated_path = path_core[max_x_idx:] + path_core[:max_x_idx]
                rotated_path.append(rotated_path[0])
                outer_toolpaths[i] = (name, rotated_path, is_outer, has_tabs, spec_z)

        # Enforce Milling Direction (Climb vs Conventional)
        def is_ccw_path(path_list):
            if not path_list or len(path_list) < 3: return True
            area = 0
            for i in range(len(path_list)-1):
                area += (path_list[i+1][0] - path_list[i][0]) * (path_list[i+1][1] + path_list[i][1])
            return area < 0

        for i in range(len(outer_toolpaths)):
            name, path, is_outer, has_tabs, spec_z = outer_toolpaths[i]
            if path and len(path) > 2 and np.allclose(path[0], path[-1]):
                target_ccw = milling_dir.startswith('Climb')
                if is_ccw_path(path) != target_ccw:
                    outer_toolpaths[i] = (name, path[::-1], is_outer, has_tabs, spec_z)

        for i in range(len(inner_toolpaths)):
            name, path, is_outer, has_tabs, spec_z = inner_toolpaths[i]
            if path and len(path) > 2 and np.allclose(path[0], path[-1]):
                target_ccw = milling_dir.startswith('Conventional')
                if is_ccw_path(path) != target_ccw:
                    inner_toolpaths[i] = (name, path[::-1], is_outer, has_tabs, spec_z)


        # --- Prepare Exclusion Zones for Outer Tabs ---
        exclusion_zones_x = []
        # 1. LE / TE (First and last 30mm of rib)
        rib_min_x, rib_max_x = 0.0, 0.0
        if poly_rib and poly_rib.is_valid:
            bounds = poly_rib.bounds
            rib_min_x, rib_max_x = bounds[0], bounds[2]
            exclusion_zones_x.append((rib_min_x - 1000.0, rib_min_x + 30.0))
            exclusion_zones_x.append((rib_max_x - 30.0, rib_max_x + 1000.0))
            
        # 2. Stringers (±10mm)
        if hasattr(rib_res, 'stringer_pts_list') and rib_res.stringer_pts_list:
            for st_pts in rib_res.stringer_pts_list:
                s_pts = [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in st_pts]
                if s_pts:
                    min_sx = min(p[0] for p in s_pts)
                    max_sx = max(p[0] for p in s_pts)
                    exclusion_zones_x.append((min_sx - 10.0, max_sx + 10.0))
                    
        # 3. Plank Steps (±10mm)
        if hasattr(rib_res, 'plank_poly_rot'):
            p_arr = rib_res.plank_poly_rot
            if len(p_arr) > 0:
                p_min_x = min(p[0] for p in p_arr) - origin_pt[0]
                p_max_x = max(p[0] for p in p_arr) - origin_pt[0]
                exclusion_zones_x.append((p_min_x - 10.0, p_min_x + 10.0))
                exclusion_zones_x.append((p_max_x - 10.0, p_max_x + 10.0))

        # Inner toolpaths first, then outer toolpath
        all_toolpaths = inner_toolpaths + outer_toolpaths
        for name, path, is_outer, has_tabs, specific_z in all_toolpaths:
            gcode.append(f"\n; --- Cutting {name} ---")
            
            # Resample the path to 1mm resolution
            dense_path = self.resample_path(path, spacing=1.0)
            if not dense_path:
                continue
                
            # If the path is closed, close it exactly
            if np.allclose(dense_path[0], dense_path[-1]):
                dense_path[-1] = dense_path[0]
                
            # --- Outer Tab Generation ---
            current_tab_centers = shifted_tab_centers
            if is_outer and tabs_active and outer_tab_interval > 0:
                current_tab_centers = []
                path_len = len(dense_path)
                num_tabs = int(path_len / outer_tab_interval)
                if num_tabs > 0:
                    step = path_len // num_tabs
                    for t_idx in range(step // 2, path_len, step):
                        # Find a valid index avoiding exclusions
                        valid_pt = None
                        search_range = step // 2
                        for offset in range(search_range):
                            for sign in (1, -1):
                                test_idx = t_idx + sign * offset
                                if 0 <= test_idx < path_len:
                                    pt_x = dense_path[test_idx][0]
                                    in_exclusion = False
                                    for ex_min, ex_max in exclusion_zones_x:
                                        if ex_min <= pt_x <= ex_max:
                                            in_exclusion = True
                                            break
                                    if not in_exclusion:
                                        valid_pt = dense_path[test_idx]
                                        break
                            if valid_pt:
                                break
                        if valid_pt:
                            current_tab_centers.append((valid_pt[0], valid_pt[1]))
            # --------------------------

            start_pt = dense_path[0]
            gcode.append(f"G0 X{start_pt[0]:.3f} Y{start_pt[1]:.3f} Z{safe_z:.3f}")
            gcode.append(f"G1 Z2.000 F1000.0 ; Plunge to start height")

            # Determine Z for first point
            cur_tab_w = outer_tab_w if is_outer else tab_width
            
            def get_target_z(x, y):
                if specific_z is not None:
                    return specific_z
                if has_tabs and tabs_active:
                    return self.get_z_at_point(x, y, current_tab_centers, cur_tab_w, cut_z, tab_z, is_outer, spar_x_coords, 0.0, tab_angle_deg)
                return cut_z

            target_z = get_target_z(start_pt[0], start_pt[1])
            gcode.append(f"G1 Z{target_z:.3f} F500.0 ; Plunge to cut depth")

            # Cut along path
            for pt in dense_path[1:]:
                target_z = get_target_z(pt[0], pt[1])
                gcode.append(f"G1 X{pt[0]:.3f} Y{pt[1]:.3f} Z{target_z:.3f} F{feed_rate:.1f}")

            # Raise tool back to safe height
            gcode.append(f"G0 Z{safe_z:.3f} ; Retract")

        # End program
        gcode.append("\n; --- Program End ---")
        gcode.append("M5 ; Spindle OFF")
        gcode.append("G0 X0.000 Y0.000 Z5.000 ; Move back to origin")
        gcode.append("M30 ; End of program")

        return "\n".join(gcode), warnings
