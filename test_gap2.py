from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np

# Rib exterior
rib = Polygon([(-20,0), (20,0), (20,10), (-20,10)])

w = 2.0
h_bar = 5.0
d_m = 10.0 # gap = 3.0
x_coords = [-d_m/2, 0, d_m/2]

bar = Polygon([(-d_m/2 - w/2, 10 + h_bar), (d_m/2 + w/2, 10 + h_bar), 
               (d_m/2 + w/2, 10 + h_bar + w), (-d_m/2 - w/2, 10 + h_bar + w)])
legs = []
for x in x_coords:
    legs.append(Polygon([(x - w/2, 9), (x + w/2, 9), (x + w/2, 10 + h_bar), (x - w/2, 10 + h_bar)]))

e_shape = unary_union([bar] + legs)
poly_rib = unary_union([rib, e_shape])

tool_radius = 1.0 # 2mm tool
offset = poly_rib.buffer(tool_radius)

print("Offset interiors:")
for i, interior in enumerate(offset.interiors):
    print(f"Interior {i}: {list(interior.coords)}")

