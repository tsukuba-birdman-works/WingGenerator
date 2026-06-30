from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np

# Rib exterior
rib = Polygon([(-20,0), (20,0), (20,10), (-20,10)])

# E-Shape
w = 2.0
h_bar = 5.0
d_m = 10.0 # gap = 5 - 2 = 3.0. Tool dia = 2.0. Will it fit?
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

print("Number of interior rings in offset:", len(offset.interiors))
print("Offset area:", offset.area)
print("Rib area:", poly_rib.area)

# Check if the boundary dips below the bar
y_vals = [p[1] for p in offset.exterior.coords]
print("Min Y on top side:", min(y for y in y_vals if y > 0))

# Try with a small d_m
d_m = 5.0 # gap = 2.5 - 2.0 = 0.5
x_coords = [-d_m/2, 0, d_m/2]
bar = Polygon([(-d_m/2 - w/2, 10 + h_bar), (d_m/2 + w/2, 10 + h_bar), 
               (d_m/2 + w/2, 10 + h_bar + w), (-d_m/2 - w/2, 10 + h_bar + w)])
legs = []
for x in x_coords:
    legs.append(Polygon([(x - w/2, 9), (x + w/2, 9), (x + w/2, 10 + h_bar), (x - w/2, 10 + h_bar)]))

e_shape2 = unary_union([bar] + legs)
poly_rib2 = unary_union([rib, e_shape2])
offset2 = poly_rib2.buffer(tool_radius)
y_vals2 = [p[1] for p in offset2.exterior.coords]
print("Small d_m Min Y on top side:", min(y for y in y_vals2 if y > 0))

