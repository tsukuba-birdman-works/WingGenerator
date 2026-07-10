import numpy as np
import trimesh

coords = np.array([[0,0,0], [1,0,0], [1,0,1], [0,0,1], [0,0,0]])
curve1 = coords
curve2 = coords + np.array([0,1,0])

num_pts = len(curve1)
faces = []
for i in range(1):
    for j in range(num_pts - 1):
        idx = i * num_pts + j
        next_idx = (i + 1) * num_pts + j
        faces.append([idx, idx + 1, next_idx + 1])
        faces.append([idx, next_idx + 1, next_idx])

vertices = np.vstack([curve1, curve2])
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

print("Original Faces normal [0]:", mesh.face_normals[0])
print("Original Faces normal [1]:", mesh.face_normals[1])
