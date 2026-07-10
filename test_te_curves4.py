import sys
import os
sys.path.append(os.getcwd())
import json
from core.engine import RibGeneratorEngine
from utils.config import ConfigHelper

conf = ConfigHelper()
params = conf.load()
# We need to fill in defaults or something, maybe just use dummy data if it fails
print("y_positions:", len(params.get('y_positions', [])))

engine = RibGeneratorEngine()
te_lens = []
for i, y_local in enumerate(params.get('y_positions', [])):
    res = engine.generate_rib_at_y(params, y_local, i, params.get('rib_thick', 2.0), False, None)
    te_lens.append(len(res[14]))

print("Lengths:", te_lens)
