import numpy as np
import trimesh
from core.export_3d import Wing3DExporter

r1 = np.array([[0, 0], [30, 0], [30, 3], [0, 3]])
r2 = np.array([[100, 0], [110, 0], [110, 1], [100, 1]])
r3 = np.array([[200, 0], [205, 0], [205, 0.5], [200, 0.5]])

c_curves = [
    np.insert(r1, 1, 0, axis=1),
    np.insert(r2, 1, 100, axis=1),
    np.insert(r3, 1, 200, axis=1)
]

mesh = Wing3DExporter.generate_lofted_surface(c_curves)
print("Mesh faces:", len(mesh.faces))
mesh.export("scratch/test_loft_out.glb")
print("Saved to scratch/test_loft_out.glb")
