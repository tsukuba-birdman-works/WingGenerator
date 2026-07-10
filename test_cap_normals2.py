import numpy as np
import trimesh
from shapely.geometry import Polygon

# CW square in XZ plane
coords = np.array([[0,0,0], [0,0,1], [1,0,1], [1,0,0], [0,0,0]])
poly_2d = Polygon(coords[:, [0, 2]]).buffer(0)
v, f = trimesh.creation.triangulate_polygon(poly_2d)

v_3d = np.zeros((len(v), 3))
v_3d[:, 0] = v[:, 0]
v_3d[:, 1] = coords[0, 1]  # Y is constant
v_3d[:, 2] = v[:, 1]

mesh_normal = trimesh.Trimesh(vertices=v_3d, faces=f)
print("CW Normal without flip:", mesh_normal.face_normals[0])
