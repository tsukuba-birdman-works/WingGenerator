import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# Dummy airfoil
l_x = np.linspace(0, 100, 10)
l_y = np.linspace(0, 0, 10)  # Flat bottom at y=0
u_x = np.linspace(100, 0, 10)
u_y = np.linspace(20, 20, 10) # Flat top at y=20
rib_pts = list(zip(u_x, u_y)) + list(zip(l_x, l_y))
rib_poly = Polygon(rib_pts)

# Dummy spar
spar_x = 30
spar_y = 10
R = 5

# Cutout 60%
cutout = box(spar_x - 0.6*R, spar_y - R, spar_x + 0.6*R, spar_y + 0.2*R)

# Pillar
pillar = box(spar_x - R - 5, -20, spar_x + R + 5, spar_y + 0.2*R)

print("Pillar area before:", pillar.area)
pillar = pillar.difference(rib_poly)
print("Pillar area after rib diff:", pillar.area)
print("Pillar bounds after rib diff:", pillar.bounds)

