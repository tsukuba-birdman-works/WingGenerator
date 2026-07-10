import sys
import os
sys.path.append(os.getcwd())
import trimesh
from core.export_3d import Wing3DExporter

base_mesh = trimesh.creation.box(extents=(10, 10, 10))
cutter = trimesh.creation.box(extents=(10, 2, 10))
cutter.apply_translation([0, 0, 0])
# cutter shares exactly the top, bottom, front, back faces with base_mesh!

result = Wing3DExporter.blender_difference(base_mesh, [cutter])
print("Result vertices:", len(result.vertices) if result else 0)
