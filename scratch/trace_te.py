import numpy as np
import trimesh
from core.export_3d import Wing3DExporter

# Create dummy meshes for test
# TE_Skin base mesh
base_mesh = trimesh.creation.box(extents=[30, 100, 5])
base_mesh.apply_translation([185, 50, 0]) # x: 170 to 200, y: 0 to 100

# Cutter mesh (Ribs_Cutter)
# Rib ends at x=180. The cutter should pierce into the TE block.
p_simp_points = np.array([[0, -2], [180, -2], [180, 2], [0, 2]])
from shapely.geometry import Polygon, box
p_simp = Polygon(p_simp_points)

# Inflate and cut just like the script
inflated_p = p_simp.buffer(1.0)
minx, miny, maxx, maxy = p_simp.bounds
bbox = box(minx - 2.0, -9999, maxx, 9999)
inflated_p = inflated_p.intersection(bbox)

# Extrude cutter
thickness = 2.0
cutter_mesh = trimesh.creation.extrude_polygon(inflated_p, height=thickness)

# apply_transform to swap y and z, and translate to y=50
swap_yz = np.array([
    [1, 0, 0, 0],
    [0, 0, -1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1]
])
cutter_mesh.apply_transform(swap_yz)
cutter_mesh.apply_translation([0, 50, 0])

# cutter_m_list
extended_subs = []
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

extended_subs.append(sub_ext)

print("Base mesh bounds:", base_mesh.bounds)
print("Sub mesh bounds:", sub_ext.bounds)

m = Wing3DExporter.blender_difference(base_mesh, extended_subs)

print("Output mesh faces:", len(m.faces) if m else "None!")

