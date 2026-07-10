import numpy as np
from shapely.geometry import Polygon
import trimesh

# Let's mock a simple airfoil-like cap
x = np.linspace(10, 0, 25)
y_u = x * 0.1
y_l = -x * 0.1

te_u = np.column_stack((x, y_u))
te_l = np.column_stack((x[::-1], y_l[::-1]))
curve = np.vstack((te_u, te_l))

print("Curve shape:", curve.shape)
if np.allclose(curve[0], curve[-1]):
    print("First and last are closed")

poly = Polygon(curve).buffer(0)
print("Poly valid?", poly.is_valid)

try:
    v, f = trimesh.creation.triangulate_polygon(poly)
    print("Triangulation success! Faces:", len(f))
except Exception as e:
    print("Triangulation error:", e)
