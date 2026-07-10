import sys
import os
sys.path.append(os.getcwd())
import json
from core.engine import WingEngine

try:
    with open('Ribgenerator.json', 'r') as f:
        params = json.load(f)
except:
    print("Could not load params")
    sys.exit(1)

engine = WingEngine()
for i, y_local in enumerate(params['y_positions']):
    res = engine.generate_rib_at_y(params, y_local, i, params['rib_thick'], False, None)
    print(f"Rib {i}: res[14] len = {len(res[14])}")
