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

mesh = Wing3DExporter.generate_lofted_surface([curve1, curve2])

print("Is watertight:", mesh.is_watertight)
print("Volume:", mesh.volume)
print("Is winding consistent:", mesh.is_winding_consistent)
print("Faces shape:", mesh.faces.shape)

print(mesh.faces)
import trimesh.repair
trimesh.repair.fix_normals(mesh)
print("After fix_normals, Is winding consistent:", mesh.is_winding_consistent)
print("After fix_normals, Volume:", mesh.volume)
