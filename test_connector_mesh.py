import sys, numpy as np
from core.export_3d import Wing3DExporter

r_conn = 5.0
y_c = 200.0
R_main = 10.0
inner = 3.0

p_start = np.array([100.0, y_c, 0.0])
p_end_lower = np.array([0.0, y_c, -R_main + r_conn])
p_end_upper = np.array([0.0, y_c, R_main - r_conn])

conn_lower = Wing3DExporter.generate_pipe_mesh([p_start, p_end_lower], r_conn, inner)
p_mid = (p_start + p_end_lower) / 2.0
conn_upper = Wing3DExporter.generate_pipe_mesh([p_mid, p_end_upper], r_conn, inner)

import trimesh
scene = trimesh.Scene([conn_lower, conn_upper])
scene.export("scratch/y_shape_test.glb")
print(f"Exported Y-Shape: lower={len(conn_lower.faces)}, upper={len(conn_upper.faces)}")
