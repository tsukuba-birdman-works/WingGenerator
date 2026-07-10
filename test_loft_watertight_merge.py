import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import trimesh
from core.export_3d import Wing3DExporter
from shapely.geometry import Polygon

# create a simple TE curve (a triangle: trailing edge is sharp, front is flat)
curve1 = np.array([
    [-10, 0, 1],
    [-10, 0, -1],
    [0, 0, 0],
    [-10, 0, 1]
])
curve2 = np.array([
    [-10, 100, 1],
    [-10, 100, -1],
    [0, 100, 0],
    [-10, 100, 1]
])

def mock_generate_lofted_surface(curves_3d):
    num_pts = len(curves_3d[0])
    aligned_curves = curves_3d
    vertices = np.vstack(aligned_curves)
    faces = []
    for i in range(len(aligned_curves) - 1):
        for j in range(num_pts - 1):
            idx = i * num_pts + j
            next_idx = (i + 1) * num_pts + j
            faces.append([idx, next_idx + 1, idx + 1])
            faces.append([idx, next_idx, next_idx + 1])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    def make_cap(curve_3d, flip_normal=False):
        poly_2d = Polygon(curve_3d[:, [0, 2]]).buffer(0)
        if poly_2d.is_empty: return None
        v, f = trimesh.creation.triangulate_polygon(poly_2d)
        v_3d = np.zeros((len(v), 3))
        v_3d[:, 0] = v[:, 0]
        v_3d[:, 1] = curve_3d[0, 1]
        v_3d[:, 2] = v[:, 1]
        if flip_normal: f = np.fliplr(f)
        return trimesh.Trimesh(vertices=v_3d, faces=f)

    cap1 = make_cap(aligned_curves[0], flip_normal=False)
    cap2 = make_cap(aligned_curves[-1], flip_normal=True)

    meshes = [mesh]
    if cap1: meshes.append(cap1)
    if cap2: meshes.append(cap2)

    final_mesh = trimesh.util.concatenate(meshes)
    final_mesh.merge_vertices()
    return final_mesh

mesh = mock_generate_lofted_surface([curve1, curve2])

print("Is watertight:", mesh.is_watertight)
print("Volume:", mesh.volume)
print("Is winding consistent:", mesh.is_winding_consistent)

# Try original normals to see if they are consistent!
def mock_generate_lofted_surface_orig(curves_3d):
    num_pts = len(curves_3d[0])
    aligned_curves = curves_3d
    vertices = np.vstack(aligned_curves)
    faces = []
    for i in range(len(aligned_curves) - 1):
        for j in range(num_pts - 1):
            idx = i * num_pts + j
            next_idx = (i + 1) * num_pts + j
            faces.append([idx, idx + 1, next_idx + 1])
            faces.append([idx, next_idx + 1, next_idx])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    def make_cap(curve_3d, flip_normal=False):
        poly_2d = Polygon(curve_3d[:, [0, 2]]).buffer(0)
        if poly_2d.is_empty: return None
        v, f = trimesh.creation.triangulate_polygon(poly_2d)
        v_3d = np.zeros((len(v), 3))
        v_3d[:, 0] = v[:, 0]
        v_3d[:, 1] = curve_3d[0, 1]
        v_3d[:, 2] = v[:, 1]
        if flip_normal: f = np.fliplr(f)
        return trimesh.Trimesh(vertices=v_3d, faces=f)

    cap1 = make_cap(aligned_curves[0], flip_normal=True)
    cap2 = make_cap(aligned_curves[-1], flip_normal=False)

    meshes = [mesh]
    if cap1: meshes.append(cap1)
    if cap2: meshes.append(cap2)

    final_mesh = trimesh.util.concatenate(meshes)
    final_mesh.merge_vertices()
    return final_mesh

mesh_orig = mock_generate_lofted_surface_orig([curve1, curve2])
print("Original Is watertight:", mesh_orig.is_watertight)
print("Original Volume:", mesh_orig.volume)
print("Original Is winding consistent:", mesh_orig.is_winding_consistent)

