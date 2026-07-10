import numpy as np
from shapely.geometry import Polygon
import trimesh

# Mock curves at Y=0 and Y=10
x = np.linspace(10, 0, 25)
y_u = x * 0.1
y_l = -x * 0.1
# CW points
te_u = np.column_stack((x, y_u))
te_l = np.column_stack((x[::-1], y_l[::-1]))
curve2d = np.vstack((te_u, te_l))

c1 = np.zeros((50, 3))
c1[:, 0] = curve2d[:, 0]
c1[:, 2] = curve2d[:, 1]
c1[:, 1] = 0

c2 = c1.copy()
c2[:, 1] = 10

def make_cap(curve_3d, flip_normal=False):
    poly_2d = Polygon(curve_3d[:, [0, 2]]).buffer(0)
    v, f = trimesh.creation.triangulate_polygon(poly_2d)
    v_3d = np.zeros((len(v), 3))
    v_3d[:, 0] = v[:, 0]
    v_3d[:, 1] = curve_3d[0, 1]
    v_3d[:, 2] = v[:, 1]
    if flip_normal: f = np.fliplr(f)
    return trimesh.Trimesh(vertices=v_3d, faces=f)

cap1 = make_cap(c1, flip_normal=False)
cap2 = make_cap(c2, flip_normal=True)

print("Cap1 (Y=0) normals:", cap1.face_normals[0])
print("Cap2 (Y=10) normals:", cap2.face_normals[0])

# Walls
faces = []
for j in range(49):
    p1 = j; p2 = j+1; p3 = j+50; p4 = j+51
    faces.append([p1, p2, p3])
    faces.append([p3, p2, p4])
walls = trimesh.Trimesh(vertices=np.vstack((c1, c2)), faces=faces)

print("Walls normal at top:", walls.face_normals[10]) # Should be +Z

mesh = trimesh.util.concatenate([walls, cap1, cap2])
mesh.merge_vertices()
print("Is mesh watertight?", mesh.is_watertight)
print("Mesh volume:", mesh.volume)
