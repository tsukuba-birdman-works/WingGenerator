from shapely.geometry import Polygon, Point
import trimesh
import numpy as np

poly = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
cutter_in = Point(50, 25).buffer(10)
diff_in = poly.difference(cutter_in)

# Simulate build_scene_geoms
mesh = trimesh.creation.extrude_polygon(diff_in, height=1.0)
print("Mesh is watertight:", mesh.is_watertight)
print("Mesh volume:", mesh.volume)
expected_volume = (100*50 - np.pi*10**2) * 1.0
print("Expected volume:", expected_volume)
print("Difference:", abs(mesh.volume - expected_volume))
