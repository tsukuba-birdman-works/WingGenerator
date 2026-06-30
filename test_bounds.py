import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.engine import RibGeneratorEngine
import numpy as np

engine = RibGeneratorEngine()
engine.update_parameters(y_positions=[0.0, 100.0], chords=[200.0, 200.0], twists=[0.0, 0.0])
engine.generate_ribs()
res = engine.rib_results[0]
rib_pts = res.final_rib_mod

# 3D conversion: x=x, y=y_ext, z=y
z_coords = rib_pts[:, 1]
print("Z min:", np.min(z_coords))
print("Z max:", np.max(z_coords))
print("Z mean:", np.mean(z_coords))
print("Z bounds center:", (np.min(z_coords) + np.max(z_coords)) / 2.0)
print("Trailing edge Z (last point):", z_coords[-1])
print("Leading edge Z (first point):", z_coords[0])
