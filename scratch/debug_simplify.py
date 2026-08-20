import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine
from utils.config import ConfigHelper
from shapely.geometry import Polygon

engine = RibGeneratorEngine()
cfg = ConfigHelper().load()
# We don't have the user's config, so let's just make a basic one
import ui.builder_vars as bv
class MockParams:
    pass
params = MockParams()
params.chord = 200
params.spar_pct = 0.3
params.spar_dia = 10
params.truss_front_margin = 5
params.truss_rear_margin = 5
params.truss_holes_count = 5
params.st_upper = [(0.2, 5, 5)]
params.st_lower = [(0.2, 5, 5)]
params.washout = 0
params.blend_enabled = False
params.fast_mode = False
params.truss_angles_dict = {}
params.base_truss_angle = 60

try:
    res = engine.generate_rib_at_y(vars(params), 0.0)
    holes = []
    if getattr(res, 'hole_m', None) is not None and len(res.hole_m) > 2: holes.append(res.hole_m)
    poly = Polygon(res.final_rib_mod, holes).buffer(0)
    print("Original points in exterior:", len(poly.exterior.coords))
    poly = poly.simplify(0.2)
    print("Simplified points in exterior:", len(poly.exterior.coords))
except Exception as e:
    print("Error:", e)
