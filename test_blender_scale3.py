import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import trimesh
from core.export_3d import Wing3DExporter
from shapely.geometry import Polygon

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

def generate_mesh(curves):
    num_pts = len(curves[0])
    vertices = np.vstack(curves)
    faces = []
    for i in range(len(curves) - 1):
        for j in range(num_pts - 1):
            idx = i * num_pts + j
            next_idx = (i + 1) * num_pts + j
            faces.append([idx, next_idx + 1, idx + 1])
            faces.append([idx, next_idx, next_idx + 1])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    def make_cap(curve_3d, flip_normal=False):
        poly_2d = Polygon(curve_3d[:, [0, 2]]).buffer(0)
        v, f = trimesh.creation.triangulate_polygon(poly_2d)
        v_3d = np.zeros((len(v), 3))
        v_3d[:, 0] = v[:, 0]
        v_3d[:, 1] = curve_3d[0, 1]
        v_3d[:, 2] = v[:, 1]
        if flip_normal: f = np.fliplr(f)
        return trimesh.Trimesh(vertices=v_3d, faces=f)

    cap1 = make_cap(curves[0], flip_normal=False)
    cap2 = make_cap(curves[-1], flip_normal=True)
    m = trimesh.util.concatenate([mesh, cap1, cap2])
    m.merge_vertices()
    return m

base_mesh = generate_mesh([curve1, curve2])
cutter = trimesh.creation.box(extents=(10.01, 10.0, 10.05))
cutter.apply_translation([-5, 50, 0])

result = Wing3DExporter.blender_difference(base_mesh, [cutter])
print("Result vertices:", len(result.vertices) if result else 0)
