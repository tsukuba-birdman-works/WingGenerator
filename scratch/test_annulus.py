import trimesh
mesh = trimesh.creation.annulus(r_min=5, r_max=10, height=20)
print(f"Bounds: {mesh.bounds}")
