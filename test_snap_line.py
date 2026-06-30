from shapely.geometry import Polygon, Point, LineString
import numpy as np

poly_rib = Polygon([(0,0), (100,0), (100,20), (0,20)])
pt_s = Point(110, 10)
pad_r = 5.0
tool_radius = 1.0

circle_s = pt_s.buffer(pad_r)
vx, vy = 100 - 110, 10 - 10
dist = 10.0
ux, uy = vx/dist, vy/dist
nx, ny = -uy, ux
p1 = (pt_s.x + nx * pad_r, pt_s.y + ny * pad_r)
p2 = (pt_s.x - nx * pad_r, pt_s.y - ny * pad_r)
p3 = (100 - nx * pad_r + ux * 2, 10 - ny * pad_r + uy * 2)
p4 = (100 + nx * pad_r + ux * 2, 10 + ny * pad_r + uy * 2)

bridge_rect = Polygon([p1, p2, p3, p4])
from shapely.ops import unary_union
bridge_full = unary_union([circle_s, bridge_rect])

original_offset_poly = poly_rib.buffer(tool_radius)

# Get the snap line on the offset path
snap_geom = original_offset_poly.exterior.intersection(bridge_full.buffer(0.1))
print("Intersection type:", snap_geom.geom_type)
if snap_geom.geom_type == "MultiLineString":
    for g in snap_geom.geoms:
        print("  Length:", g.length, "Coords:", list(g.coords))
elif snap_geom.geom_type == "LineString":
    print("  Length:", snap_geom.length, "Coords:", list(snap_geom.coords))

