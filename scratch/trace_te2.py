import numpy as np
import trimesh
from core.export_3d import Wing3DExporter

# TE_Skin base mesh from Y=0 to Y=100
base_mesh = trimesh.creation.box(extents=[30, 100, 5])
base_mesh.apply_translation([185, 50, 0]) # x: 170 to 200, y: 0 to 100

p_simp_points = np.array([[0, -2], [180, -2], [180, 2], [0, 2]])
from shapely.geometry import Polygon, box
p_simp = Polygon(p_simp_points)

inflated_p = p_simp.buffer(1.0)
minx, miny, maxx, maxy = p_simp.bounds
bbox = box(minx - 2.0, -9999, maxx, 9999)
inflated_p = inflated_p.intersection(bbox)

cutter_mesh = trimesh.creation.extrude_polygon(inflated_p, height=2.0)

swap_yz = np.array([
    [1, 0, 0, 0],
    [0, 0, -1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1]
])
cutter_mesh.apply_transform(swap_yz)

# Cutter for Rib 0 is at Y=0 (Y=0 to 2 originally)
cutter_mesh.apply_translation([0, 0, 0])

sub_ext = cutter_mesh.copy()
y_min, y_max = sub_ext.bounds[:, 1]
y_center = (y_min + y_max) / 2.0
t = y_max - y_min
scale = (t + 2.0) / t

t1 = np.eye(4)
t1[1, 3] = -y_center
s_mat = np.eye(4)
s_mat[1, 1] = scale
t2 = np.eye(4)
t2[1, 3] = y_center
mat = t2 @ s_mat @ t1
sub_ext.apply_transform(mat)

m = Wing3DExporter.blender_difference(base_mesh, [sub_ext])
print("Output mesh faces:", len(m.faces) if m else "None!")

