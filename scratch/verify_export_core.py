import json
import traceback
import numpy as np
import trimesh
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder

def run():
    with open('preset/test.json', 'r') as f:
        data = json.load(f)

    data['y_positions'] = [0, 50, 100, 150, 200]
    data['export_te'] = True
    data['wing_type'] = "Right"

    engine = RibGeneratorEngine()
    
    # Let's bypass UI params and construct enough for _collect_geometry_data
    # Actually, we can just run engine.export_3d_data(data)
    try:
        res = engine.export_3d_data(data)
    except Exception as e:
        print("export_3d_data failed:", e)
        # We need ALL the params to be exactly correct.
        
run()
