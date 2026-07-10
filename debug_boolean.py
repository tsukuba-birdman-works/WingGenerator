import sys
import numpy as np
import trimesh

# Let's create a dummy TE Skin and a dummy rib cutter
# TE Skin: Box from x=-10 to x=0, y=0 to y=202, z=-2 to z=2
te_skin = trimesh.creation.box(extents=[10, 202, 4], transform=trimesh.transformations.translation_matrix([-5, 101, 0]))

# Rib cutter 1 (middle): y=100 to y=102
cutter1 = trimesh.creation.box(extents=[10, 4, 10], transform=trimesh.transformations.translation_matrix([-10, 101, 0]))
# shift X by +0.5
cutter1.apply_translation([0.5, 0, 0])

# Rib cutter 2 (tip): y=200 to y=202
cutter2 = trimesh.creation.box(extents=[10, 4, 10], transform=trimesh.transformations.translation_matrix([-10, 201, 0]))
# shift X by +0.5
cutter2.apply_translation([0.5, 0, 0])

combined_sub = trimesh.util.concatenate([cutter1, cutter2])

from core.export_3d import Wing3DExporter
try:
    res = Wing3DExporter.blender_difference(te_skin, combined_sub)
    res.export('debug_boolean_te.glb')
    print("Exported debug_boolean_te.glb")
except Exception as e:
    print("Error:", e)
