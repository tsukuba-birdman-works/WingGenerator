import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine
import numpy as np
import shapely.geometry as sg
engine = RibGeneratorEngine()

inner_poly = sg.Polygon([(0,0), (100,0), (100,50), (0,50)])
blocks_f = [[ ((40,0), (40,50)), ((30,0), (30,50)), ((10,0), (10,50)) ]]
blocks_r = [[ ((70,0), (70,50)), ((90,0), (90,50)) ]]
R_mat = np.eye(2)
spar_x, spar_y = 50, 25

polys = engine.process_blocks_sharp(blocks_f, blocks_r, R_mat, spar_x, spar_y, inner_poly, 2.0)
for poly, is_rear, idx in polys:
    print(f"Centroid={poly.centroid.x}, is_rear={is_rear}, idx={idx}")
