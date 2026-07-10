import sys
import os
sys.path.append(os.getcwd())
from core.export_3d import Wing3DExporter
from core.engine import WingEngine
import json

# Load user parameters from the default output or test
try:
    with open('Ribgenerator.json', 'r') as f:
        params = json.load(f)
except:
    print("Could not load params")
    sys.exit(1)

# Just run a quick check on the lengths of te_curves
engine = WingEngine()
te_curves = []
for i, y_local in enumerate(params['y_positions']):
    res = engine.generate_rib_at_y(params, y_local, i, params['rib_thick'], False, None)
    if len(res[14]) > 0:
        te_curves.append(res[14])

lens = [len(c) for c in te_curves]
print("Lengths of te_curves:", lens)
print("Max length:", max(lens) if lens else 0)
