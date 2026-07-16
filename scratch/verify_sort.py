from shapely.geometry import Polygon, Point
polys = [
    Polygon([(0,0), (1,0), (1,1), (0,1)]),
    Polygon([(-2,0), (-1,0), (-1,1), (-2,1)])
]
spar_x = 2
sorted_polys = sorted(polys, key=lambda p: abs(p.centroid.x - spar_x))
for p in sorted_polys:
    print(p.centroid.x)
