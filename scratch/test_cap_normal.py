import numpy as np
from shapely.geometry import Polygon
import trimesh

# Create a CCW polygon
pts = [(0,0), (10,0), (10,10), (0,10)]
poly = Polygon(pts)

v, f = trimesh.creation.triangulate_polygon(poly)
v_3d = np.zeros((len(v), 3))
v_3d[:, 0] = v[:, 0]
v_3d[:, 2] = v[:, 1]
mesh = trimesh.Trimesh(vertices=v_3d, faces=f)
print("Normals of CCW poly:")
print(mesh.face_normals)

