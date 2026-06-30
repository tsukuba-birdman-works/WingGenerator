import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

rib_pts = []
for x in np.linspace(-30, 30, 50):
    rib_pts.append((x, 20 - x**2/100)) # Curve from (0,20) down to (-30,11)
rib_pts.extend([(30,0), (-30,0)])
poly_rib = Polygon(rib_pts)

c_m = np.array([0.0, 10.0])
d_m = 20.0
w = 2.0
h_bar = 5.0
x_coords = [c_m[0] - d_m/2, c_m[0], c_m[0] + d_m/2]
minx, miny, maxx, maxy = poly_rib.bounds

top_y_vals = []
for x in x_coords:
    v_line = LineString([(x, miny - 10), (x, maxy + 10)])
    inter = poly_rib.exterior.intersection(v_line)
    if not inter.is_empty:
        pts = [inter.y] if inter.geom_type == 'Point' else [p.y for p in inter.geoms if p.geom_type == 'Point']
        if pts: top_y_vals.append(max(pts))

if len(top_y_vals) == 3:
    # Tilted bar
    bottom_pts = [(x, y + h_bar) for x, y in zip(x_coords, top_y_vals)]
    top_pts = [(x, y + h_bar + w) for x, y in zip(reversed(x_coords), reversed(top_y_vals))]
    
    # We need to extend the bar slightly left and right by w/2 so the outer legs are fully covered.
    # The slope at the left:
    dx_l = x_coords[1] - x_coords[0]
    dy_l = top_y_vals[1] - top_y_vals[0]
    slope_l = dy_l / dx_l
    left_x = x_coords[0] - w/2
    left_y_bot = top_y_vals[0] + h_bar - (w/2)*slope_l
    left_y_top = top_y_vals[0] + h_bar + w - (w/2)*slope_l
    
    # The slope at the right:
    dx_r = x_coords[2] - x_coords[1]
    dy_r = top_y_vals[2] - top_y_vals[1]
    slope_r = dy_r / dx_r
    right_x = x_coords[2] + w/2
    right_y_bot = top_y_vals[2] + h_bar + (w/2)*slope_r
    right_y_top = top_y_vals[2] + h_bar + w + (w/2)*slope_r
    
    bar_pts = [(left_x, left_y_bot), (x_coords[1], top_y_vals[1] + h_bar), (right_x, right_y_bot),
               (right_x, right_y_top), (x_coords[1], top_y_vals[1] + h_bar + w), (left_x, left_y_top)]
               
    bar_poly = Polygon(bar_pts)
    
    leg_polys = []
    for x, y_rib in zip(x_coords, top_y_vals):
        # Leg from y_rib to bar
        leg_poly = Polygon([
            (x - w/2, y_rib - 2.0),
            (x + w/2, y_rib - 2.0),
            (x + w/2, y_rib + h_bar + 0.1),
            (x - w/2, y_rib + h_bar + 0.1)
        ])
        leg_polys.append(leg_poly)
        
    e_shape = unary_union([bar_poly] + leg_polys)
    print("E-Shape area:", e_shape.area)
    print("E-Shape is valid:", e_shape.is_valid)

