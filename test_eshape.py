import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union, nearest_points

# Dummy rib: a simple curved top surface
rib_pts = []
for x in np.linspace(-30, 30, 50):
    rib_pts.append((x, 20 - x**2/100)) # Curve from (0,20) down to (-30,11)
rib_pts.extend([(30,0), (-30,0)])
poly_rib = Polygon(rib_pts)

c_m = np.array([0.0, 10.0])
d_m = 20.0
w = 2.0  # Support width
h_bar = 5.0 # Height of the horizontal bar above the rib

# We want 3 legs at X = -d_m/2, 0, d_m/2
x_coords = [c_m[0] - d_m/2, c_m[0], c_m[0] + d_m/2]

minx, miny, maxx, maxy = poly_rib.bounds
# Find intersection of vertical lines with poly_rib.exterior to find the top surface
top_y_vals = []
for x in x_coords:
    v_line = LineString([(x, miny - 10), (x, maxy + 10)])
    inter = poly_rib.exterior.intersection(v_line)
    if not inter.is_empty:
        # Get highest Y
        if inter.geom_type == 'Point':
            top_y_vals.append(inter.y)
        elif inter.geom_type in ['MultiPoint', 'GeometryCollection']:
            pts = [p.y for p in inter.geoms if p.geom_type == 'Point']
            if pts:
                top_y_vals.append(max(pts))

if len(top_y_vals) == 3:
    max_rib_y = max(top_y_vals)
    bar_y_bottom = max_rib_y + h_bar
    bar_y_top = bar_y_bottom + w
    
    # Create the horizontal bar
    bar_rect = Polygon([
        (x_coords[0] - w/2, bar_y_bottom),
        (x_coords[-1] + w/2, bar_y_bottom),
        (x_coords[-1] + w/2, bar_y_top),
        (x_coords[0] - w/2, bar_y_top)
    ])
    
    # Create the 3 legs
    leg_polys = []
    for x, y_rib in zip(x_coords, top_y_vals):
        # Leg goes from slightly inside the rib up to the bar
        leg = Polygon([
            (x - w/2, y_rib - 2.0),
            (x + w/2, y_rib - 2.0),
            (x + w/2, bar_y_bottom + 0.1),
            (x - w/2, bar_y_bottom + 0.1)
        ])
        leg_polys.append(leg)
        
    e_shape = unary_union([bar_rect] + leg_polys)
    print("E-shape created, area:", e_shape.area)
    
    poly_rib = unary_union([poly_rib, e_shape])
    print("Combined area:", poly_rib.area)
