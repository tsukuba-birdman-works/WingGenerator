import trimesh
import numpy as np
import shapely.geometry as sg

def generate_stadium_torus_mesh(center, normal_vec, offset_y, r_pipe, wire_radius, num_pts=16):
    circle = sg.Point(0, 0).buffer(wire_radius)
    r_path = r_pipe + wire_radius
    
    path_pts = []
    # Right semicircle
    for i in range(num_pts + 1):
        angle = -np.pi/2 + np.pi * i / num_pts
        path_pts.append([0.0, offset_y + r_path * np.cos(angle), r_path * np.sin(angle)])
        
    # Left semicircle
    for i in range(num_pts + 1):
        angle = np.pi/2 + np.pi * i / num_pts
        path_pts.append([0.0, -offset_y + r_path * np.cos(angle), r_path * np.sin(angle)])
        
    path_pts.append(path_pts[0])
    path = np.array(path_pts)
    
    try:
        mesh = trimesh.creation.sweep_polygon(circle, path)
        rot = trimesh.geometry.align_vectors([1, 0, 0], normal_vec)
        mesh.apply_transform(rot)
        mesh.apply_translation(center)
        return mesh
    except Exception as e:
        print("Error:", e)
        return None

# Test with offset = 0
mesh = generate_stadium_torus_mesh([0,0,0], [1,0,0], 0.0, 3.0, 1.0)
print(len(mesh.vertices))
