import sys
import os
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine
from utils.config import ConfigHelper

conf = ConfigHelper()
try:
    params = conf.load()
except:
    pass

# We will just write a function to run via the UI's base code but skip UI
import json
try:
    with open('Ribgenerator.json', 'r') as f:
        params = json.load(f)
except:
    params = {}

if not params:
    print("No params")
    sys.exit()

engine = RibGeneratorEngine()
te_curves = []
for i, y_local in enumerate(params.get('y_positions', [])):
    res = engine.generate_rib_at_y(params, y_local, i, params.get('rib_thick', 2.0), False, None)
    if len(res[14]) > 0:
        te_curves.append(res[14])

for i, c in enumerate(te_curves):
    print(f"Rib {i} length:", len(c))
    if len(c) > 0:
        print("First 3 pts:", c[:3])
