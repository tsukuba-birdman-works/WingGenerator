import trimesh
import numpy as np

# Create a box
box = trimesh.creation.box()

# Apply PBR material
material = trimesh.visual.material.PBRMaterial(
    baseColorFactor=[50, 50, 50, 255],
    metallicFactor=0.8,
    roughnessFactor=0.2
)

# In trimesh, materials are often assigned to the visual object
# But wait, trimesh native objects usually have simple color visuals. 
# We need to ensure we use a TextureVisuals if we want to assign a Material, 
# or maybe we can just assign visual.material directly. Let's test:
try:
    box.visual.material = material
except Exception as e:
    print("Error assigning material directly:", e)

# Let's save and inspect the GLB
box.export("scratch/test_pbr.glb")
print("Exported box with PBR material.")
