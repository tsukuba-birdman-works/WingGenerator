import os
import subprocess
import csv
import numpy as np
import gmsh
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import nearest_points

def calc_polygon_inertia(pts):
    """
    Calculate area, centroid, and moments of inertia (Ixx, Iyy) about the centroid
    for an arbitrary polygon given as a list/array of (X, Y) points.
    Assumes points are ordered along the perimeter.
    """
    if len(pts) < 3:
        return 0, 0, 0, 0, 0
    
    pts = np.array(pts)
    if not np.allclose(pts[0], pts[-1]):
        pts = np.vstack((pts, pts[0]))
        
    x = pts[:, 0]
    y = pts[:, 1]
    
    # Shoelace formula for area
    a = x[:-1] * y[1:] - x[1:] * y[:-1]
    A = 0.5 * np.sum(a)
    if A == 0:
        return 0, 0, 0, 0, 0
        
    # Centroid
    Cx = np.sum((x[:-1] + x[1:]) * a) / (6.0 * A)
    Cy = np.sum((y[:-1] + y[1:]) * a) / (6.0 * A)
    
    # Moments of inertia about origin
    I_x = np.sum((y[:-1]**2 + y[:-1]*y[1:] + y[1:]**2) * a) / 12.0
    I_y = np.sum((x[:-1]**2 + x[:-1]*x[1:] + x[1:]**2) * a) / 12.0
    
    # Parallel axis theorem to get moments about centroid
    I_xx = abs(I_x - A * Cy**2)
    I_yy = abs(I_y - A * Cx**2)
    
    return abs(A), Cx, Cy, I_xx, I_yy

class RibFEAEngine:
    def __init__(self, work_dir="."):
        self.work_dir = work_dir
        self.lift_dist = None
        self.mesh_data = {}

    def load_lift_csv(self, filepath: str):
        """
        Loads CSV with columns: x_c, p_upper, p_lower
        """
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            xc_col = next((c for c in cols if 'x' in c.lower()), cols[0])
            pu_col = next((c for c in cols if 'up' in c.lower()), cols[1])
            pl_col = next((c for c in cols if 'low' in c.lower()), cols[2])
            
            for row in reader:
                try:
                    data.append({
                        'x_c': float(row[xc_col]),
                        'p_upper': float(row[pu_col]),
                        'p_lower': float(row[pl_col])
                    })
                except ValueError:
                    continue
        
        data.sort(key=lambda d: d['x_c'])
        self.lift_dist = {
            'x_c': np.array([d['x_c'] for d in data]),
            'p_upper': np.array([d['p_upper'] for d in data]),
            'p_lower': np.array([d['p_lower'] for d in data])
        }
        return self.lift_dist

    def interpolate_pressure(self, x_c, is_upper):
        if self.lift_dist is None:
            return 0.0
        p_arr = self.lift_dist['p_upper'] if is_upper else self.lift_dist['p_lower']
        return np.interp(x_c, self.lift_dist['x_c'], p_arr)

    def _shapely_to_gmsh(self, polygon: Polygon, mesh_size=2.0, plank_poly=None):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("Rib")

        def add_ring(ring):
            coords = list(ring.coords)
            
            cleaned_coords = []
            for x, y in coords:
                if not cleaned_coords:
                    cleaned_coords.append((x, y))
                else:
                    if np.hypot(x - cleaned_coords[-1][0], y - cleaned_coords[-1][1]) > 1e-3:
                        cleaned_coords.append((x, y))
            
            if len(cleaned_coords) > 1 and np.hypot(cleaned_coords[0][0] - cleaned_coords[-1][0], cleaned_coords[0][1] - cleaned_coords[-1][1]) < 1e-3:
                cleaned_coords.pop()
                
            if len(cleaned_coords) < 3:
                return None, []
                
            pt_tags = [gmsh.model.occ.addPoint(x, y, 0, mesh_size) for x, y in cleaned_coords]
            line_tags = []
            for i in range(len(pt_tags)):
                try:
                    line_tags.append(gmsh.model.occ.addLine(pt_tags[i], pt_tags[(i+1)%len(pt_tags)]))
                except Exception:
                    pass
                    
            if not line_tags: return None, []
            
            try:
                cl = gmsh.model.occ.addCurveLoop(line_tags)
                return cl, line_tags
            except Exception:
                return None, []

        def build_surface(poly):
            cl_outer, outer_lines = add_ring(poly.exterior)
            if cl_outer is None: return None, [], []
            holes_lines = []
            cl_holes = []
            for interior in poly.interiors:
                cl, lines = add_ring(interior)
                if cl is not None:
                    cl_holes.append(cl)
                    holes_lines.extend(lines)
            surf = gmsh.model.occ.addPlaneSurface([cl_outer] + cl_holes)
            return surf, outer_lines, holes_lines

        surf_rib, outer_lines_rib, holes_lines = build_surface(polygon)
        surfs_to_frag = [(2, surf_rib)] if surf_rib is not None else []
        
        if plank_poly is not None and not plank_poly.is_empty:
            surf_plank, _, _ = build_surface(plank_poly)
            if surf_plank is not None:
                surfs_to_frag.append((2, surf_plank))
                
        if len(surfs_to_frag) > 1:
            out, out_map = gmsh.model.occ.fragment([surfs_to_frag[0]], surfs_to_frag[1:])
            
            plank_surfs_set = set(tag for dim, tag in out_map[1])
            rib_surfs = [tag for dim, tag in out_map[0] if tag not in plank_surfs_set]
            plank_surfs = list(plank_surfs_set)
        else:
            rib_surfs = [surf_rib] if surf_rib is not None else []
            plank_surfs = []

        gmsh.model.occ.synchronize()

        if rib_surfs:
            gmsh.model.addPhysicalGroup(2, rib_surfs, 1, name="RIB_SOLID")
        if plank_surfs:
            gmsh.model.addPhysicalGroup(2, plank_surfs, 2, name="PLANK_SOLID")
            
        # Physical groups for boundaries (simplified, just grab all boundaries of rib)
        if surf_rib is not None:
            # We can just add all lines of rib_surfs to physical groups
            bnd = gmsh.model.getBoundary([(2, t) for t in rib_surfs])
            bnd_tags = [t[1] for t in bnd]
            if bnd_tags:
                gmsh.model.addPhysicalGroup(1, bnd_tags, 3, name="RibBoundary")
            
        gmsh.model.mesh.generate(2)

        nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()
        coords = np.array(nodeCoords).reshape(-1, 3)
        
        # Collect elements by physical group
        tri_tags_rib, tri_nodes_rib = [], []
        tri_tags_plank, tri_nodes_plank = [], []
        
        def get_elems(phys_tag):
            try:
                ent = gmsh.model.getEntitiesForPhysicalGroup(2, phys_tag)
            except Exception:
                ent = []
            t_tags, t_nodes = [], []
            for e in ent:
                elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(2, e)
                for etype, etags, enodes in zip(elemTypes, elemTags, elemNodeTags):
                    if etype == 2:
                        t_tags.extend(etags)
                        t_nodes.extend(np.array(enodes).reshape(-1, 3))
            return t_tags, t_nodes

        tri_tags_rib, tri_nodes_rib = get_elems(1)
        tri_tags_plank, tri_nodes_plank = get_elems(2)
        
        # Determine outer and hole nodes geometrically
        aero_poly = polygon
        if plank_poly is not None and not plank_poly.is_empty:
            aero_poly = polygon.union(plank_poly)
            
        outer_line = aero_poly.exterior
        hole_lines = aero_poly.interiors
        
        outer_nodes_set = set()
        hole_nodes_set = set()
        
        for tag, (x, y, z) in zip(nodeTags, coords):
            pt = Point(x, y)
            if outer_line.distance(pt) < 1e-3:
                outer_nodes_set.add(tag)
            else:
                for h in hole_lines:
                    if h.distance(pt) < 1e-3:
                        hole_nodes_set.add(tag)
                        break

        # Determine used nodes
        used_nodes_set = set(np.array(tri_nodes_rib).flatten()) if len(tri_nodes_rib) > 0 else set()
        if len(tri_nodes_plank) > 0:
            used_nodes_set.update(np.array(tri_nodes_plank).flatten())
            
        self.mesh_data = {
            'nodeTags': np.array(nodeTags),
            'nodeCoords': coords,
            'triTagsRib': np.array(tri_tags_rib),
            'triNodesRib': np.array(tri_nodes_rib),
            'triTagsPlank': np.array(tri_tags_plank),
            'triNodesPlank': np.array(tri_nodes_plank),
            'triTags': np.array(tri_tags_rib + tri_tags_plank),
            'triNodes': np.array(tri_nodes_rib + tri_nodes_plank),
            'outerNodes': outer_nodes_set.intersection(used_nodes_set),
            'holeNodes': hole_nodes_set.intersection(used_nodes_set)
        }

        gmsh.finalize()
        return self.mesh_data

    def generate_fea_model(self, polygon: Polygon, spar_centers: list, chord: float, material_props: dict, thickness: float, mesh_size=2.0, stringer_pts_list=None, stringer_params=None, plank_poly=None, plank_params=None):
        self._shapely_to_gmsh(polygon, mesh_size, plank_poly)

        inp_path = os.path.join(self.work_dir, "rib_fea.inp")
        
        E = material_props.get('E', 15.0)
        nu = material_props.get('nu', 0.3)

        fixed_nodes = []
        
        # Identify exact spar hole nodes by finding the minimum distance to spar centers
        for sx, sy in spar_centers:
            dists = []
            hole_tags = []
            for tag, coord in zip(self.mesh_data['nodeTags'], self.mesh_data['nodeCoords']):
                if tag in self.mesh_data['holeNodes']:
                    dists.append(np.hypot(coord[0]-sx, coord[1]-sy))
                    hole_tags.append(tag)
            
            if dists:
                min_dist = min(dists)
                for d, tag in zip(dists, hole_tags):
                    # 5mm tolerance for mesh polygonization
                    if d < min_dist + 5.0:
                        fixed_nodes.append(tag)
                        
        fixed_nodes = list(set(fixed_nodes))
                    
        with open(inp_path, "w") as f:
            f.write("*HEADING\nRib FEA\n")
            f.write("*NODE, NSET=NALL\n")
            
            # Filter to only used nodes to avoid singular matrix
            used_node_tags = set(self.mesh_data['triNodes'].flatten())
            
            for tag, c in zip(self.mesh_data['nodeTags'], self.mesh_data['nodeCoords']):
                if tag in used_node_tags:
                    f.write(f"{tag}, {c[0]:.6f}, {c[1]:.6f}, {c[2]:.6f}\n")
                
            f.write("*ELEMENT, TYPE=CPS3, ELSET=EALL\n")
            for tag, nodes in zip(self.mesh_data['triTags'], self.mesh_data['triNodes']):
                f.write(f"{tag}, {nodes[0]}, {nodes[2]}, {nodes[1]}\n")
                
            if fixed_nodes:
                f.write("*NSET, NSET=FIXED\n")
                for i in range(0, len(fixed_nodes), 16):
                    f.write(", ".join(map(str, fixed_nodes[i:i+16])) + "\n")

            f.write(f"*MATERIAL, NAME=MAT_RIB\n")
            f.write(f"*ELASTIC\n")
            f.write(f"{E}, {nu}\n")
            
            if len(self.mesh_data['triTagsPlank']) > 0:
                E_plank = plank_params.get('E', 3000.0) if plank_params else 3000.0
                f.write(f"*MATERIAL, NAME=MAT_PLANK\n")
                f.write(f"*ELASTIC\n")
                f.write(f"{E_plank}, {nu}\n")
            
            if len(self.mesh_data['triTagsRib']) > 0:
                f.write(f"*ELSET, ELSET=EALL_RIB\n")
                for i in range(0, len(self.mesh_data['triTagsRib']), 16):
                    f.write(", ".join(map(str, self.mesh_data['triTagsRib'][i:i+16])) + "\n")
            
            if len(self.mesh_data['triTagsPlank']) > 0:
                f.write(f"*ELSET, ELSET=EALL_PLANK\n")
                for i in range(0, len(self.mesh_data['triTagsPlank']), 16):
                    f.write(", ".join(map(str, self.mesh_data['triTagsPlank'][i:i+16])) + "\n")

            if len(self.mesh_data['triTagsRib']) > 0:
                f.write("*SOLID SECTION, ELSET=EALL_RIB, MATERIAL=MAT_RIB\n")
                f.write(f"{thickness}\n")
            
            if len(self.mesh_data['triTagsPlank']) > 0:
                f.write("*SOLID SECTION, ELSET=EALL_PLANK, MATERIAL=MAT_PLANK\n")
                if plank_params and plank_params.get('enabled', False):
                    f.write(f"{plank_params.get('width', 100.0)}\n")
                else:
                    f.write(f"{thickness}\n")
            
            # Model-level definitions (Elements, Springs, Materials, etc.) must go before *STEP
            max_elem_tag = 0
            if len(self.mesh_data['triTags']) > 0:
                max_elem_tag = int(np.max(self.mesh_data['triTags']))
            
            if stringer_pts_list and stringer_params and stringer_params.get('enabled', False):
                E_str = stringer_params.get('E', 10000.0)
                L = stringer_params.get('span_L', 1000.0)
                a = stringer_params.get('rib_pos_a', 500.0)
                b = L - a
                if a > 0 and b > 0:
                    for i, pts in enumerate(stringer_pts_list):
                        if len(pts) > 2:
                            A, Cx, Cy, Ixx, Iyy = calc_polygon_inertia(pts)
                            if Ixx > 0 and Iyy > 0:
                                ky_total = (3 * E_str * Ixx * L**3) / (a**3 * b**3)
                                kx_total = (3 * E_str * Iyy * L**3) / (a**3 * b**3)
                                
                                # Find nodes on this stringer's boundary
                                str_poly = Polygon(pts).buffer(mesh_size * 0.5)
                                str_nodes = []
                                for tag, c in zip(self.mesh_data['nodeTags'], self.mesh_data['nodeCoords']):
                                    if tag in self.mesh_data['outerNodes'] or tag in self.mesh_data['holeNodes']:
                                        if str_poly.contains(Point(c[0], c[1])):
                                            str_nodes.append(tag)
                                            
                                if len(str_nodes) > 0:
                                    kx_node = kx_total / len(str_nodes)
                                    ky_node = ky_total / len(str_nodes)
                                    
                                    # Write spring elements
                                    for node_idx, n_tag in enumerate(str_nodes):
                                        max_elem_tag += 1
                                        elem_id_x = max_elem_tag
                                        max_elem_tag += 1
                                        elem_id_y = max_elem_tag
                                        
                                        f.write(f"*ELEMENT, TYPE=SPRING1, ELSET=STR_SPR_X_{i}\n")
                                        f.write(f"{int(elem_id_x)}, {int(n_tag)}\n")
                                        f.write(f"*SPRING, ELSET=STR_SPR_X_{i}\n")
                                        f.write(f"1\n")
                                        f.write(f"{kx_node:.3f}\n")
                                        
                                        f.write(f"*ELEMENT, TYPE=SPRING1, ELSET=STR_SPR_Y_{i}\n")
                                        f.write(f"{int(elem_id_y)}, {int(n_tag)}\n")
                                        f.write(f"*SPRING, ELSET=STR_SPR_Y_{i}\n")
                                        f.write(f"2\n")
                                        f.write(f"{ky_node:.3f}\n")

            f.write("*STEP\n*STATIC\n*BOUNDARY\n")
            # Fix Z-DOF for all nodes because SPRING1 elements trigger 3D DOFs in CalculiX
            f.write("NALL, 3, 3, 0.0\n")
            
            if fixed_nodes:
                f.write("FIXED, 1, 2, 0.0\n")
            
            if self.lift_dist is not None:
                f.write("*CLOAD\n")
                
                # Determine chord line to classify upper vs lower surface accurately
                outer_coords = [c for tag, c in zip(self.mesh_data['nodeTags'], self.mesh_data['nodeCoords']) if tag in self.mesh_data['outerNodes']]
                x_min_idx = np.argmin([c[0] for c in outer_coords])
                x_max_idx = np.argmax([c[0] for c in outer_coords])
                x_le, y_le = outer_coords[x_min_idx][:2]
                x_te, y_te = outer_coords[x_max_idx][:2]
                
                exterior_coords = np.array(polygon.exterior.coords)
                # Shapely polygons have CCW exterior, outward normal is (vy, -vx)
                def get_outward_normal(px, py):
                    min_dist = float('inf')
                    best_norm = (0.0, 1.0)
                    for i in range(len(exterior_coords)-1):
                        p1 = exterior_coords[i]
                        p2 = exterior_coords[i+1]
                        vx, vy = p2[0]-p1[0], p2[1]-p1[1]
                        wx, wy = px-p1[0], py-p1[1]
                        c1 = wx*vx + wy*vy
                        c2 = vx*vx + vy*vy
                        if c1 <= 0:
                            dist = np.hypot(px-p1[0], py-p1[1])
                        elif c2 <= c1:
                            dist = np.hypot(px-p2[0], py-p2[1])
                        else:
                            b = c1 / c2
                            dist = np.hypot(px - (p1[0] + b*vx), py - (p1[1] + b*vy))
                        
                        if dist < min_dist:
                            min_dist = dist
                            length = np.hypot(vx, vy)
                            if length > 1e-6:
                                # For a clockwise polygon, outward normal is (-vy, vx)
                                best_norm = (-vy/length, vx/length)
                    return best_norm

                outer_coords_arr = np.array(outer_coords)
                for tag, c in zip(self.mesh_data['nodeTags'], self.mesh_data['nodeCoords']):
                    if tag in self.mesh_data['outerNodes']:
                        x_c = c[0] / chord
                        
                        nx, ny = get_outward_normal(c[0], c[1])
                        
                        is_upper = ny >= 0
                        p_val = self.interpolate_pressure(x_c, is_upper)
                        
                        # Calculate true tributary length
                        dists = np.hypot(outer_coords_arr[:,0] - c[0], outer_coords_arr[:,1] - c[1])
                        sorted_dists = np.sort(dists)
                        trib_len = mesh_size
                        if len(sorted_dists) > 2:
                            trib_len = 0.5 * (sorted_dists[1] + sorted_dists[2])
                        
                        if is_upper:
                            force_mag = p_val * trib_len * thickness
                        else:
                            force_mag = -p_val * trib_len * thickness
                            
                        force_x = force_mag * nx
                        force_y = force_mag * ny
                        
                        if abs(force_x) > 1e-6:
                            f.write(f"{tag}, 1, {force_x:.6f}\n")
                        if abs(force_y) > 1e-6:
                            f.write(f"{tag}, 2, {force_y:.6f}\n")
                            
            f.write("*NODE PRINT, NSET=FIXED\nRF\n")
            f.write("*NODE PRINT, NSET=NALL\nU\n")
            f.write("*EL PRINT, ELSET=EALL\nS\n")
            f.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")
            
        return inp_path
    def parse_inp_loads(self, filepath):
        loads = {}
        in_cload = False
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('*CLOAD'):
                    in_cload = True
                    continue
                if in_cload:
                    if line.startswith('*'):
                        in_cload = False
                        continue
                    parts = line.split(',')
                    if len(parts) >= 3:
                        tag = int(parts[0])
                        dof = int(parts[1])
                        val = float(parts[2])
                        if tag not in loads:
                            loads[tag] = [0.0, 0.0]
                        if dof == 1: loads[tag][0] += val
                        elif dof == 2: loads[tag][1] += val
        return loads

    def parse_dat_results(self, filepath):
        disp = {}
        stress = {}
        rf = {}
        
        mode = None
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("displacements"):
                    mode = "disp"
                    continue
                elif line.startswith("stresses"):
                    mode = "stress"
                    continue
                elif line.startswith("forces"):
                    mode = "rf"
                    continue
                    
                if not line:
                    continue
                    
                parts = line.split()
                if mode == "disp" and len(parts) >= 4:
                    try:
                        tag = int(parts[0])
                        dx = float(parts[1])
                        dy = float(parts[2])
                        dz = float(parts[3])
                        disp[tag] = (dx, dy, dz)
                    except ValueError:
                        pass
                elif mode == "rf" and len(parts) >= 4:
                    try:
                        tag = int(parts[0])
                        rfx = float(parts[1])
                        rfy = float(parts[2])
                        rf[tag] = (rfx, rfy)
                    except ValueError:
                        pass
                elif mode == "stress" and len(parts) >= 8:
                    try:
                        elem = int(parts[0])
                        ip = int(parts[1])
                        sxx = float(parts[2])
                        syy = float(parts[3])
                        sxy = float(parts[5])
                        
                        # Calculate von mises (approx for plane stress)
                        vm = np.sqrt(sxx**2 + syy**2 - sxx*syy + 3*sxy**2)
                        
                        if elem not in stress:
                            stress[elem] = []
                        stress[elem].append(vm)
                    except ValueError:
                        pass
                        
        # Average stress per element
        for k in stress:
            stress[k] = sum(stress[k]) / len(stress[k])
            
        return disp, stress, rf
