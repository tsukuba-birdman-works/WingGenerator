import numpy as np
from core.export_3d import Wing3DExporter
try:
    mesh = Wing3DExporter.generate_pipe_mesh([np.array([10.0, 10.0, 0.0]), np.array([0.0, 10.0, -5.0])], 5.0, 4.0)
    print("Pipe generated:", len(mesh.faces))
except Exception as e:
    print("Error:", e)
