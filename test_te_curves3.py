import sys
import os
sys.path.append(os.getcwd())
from core.engine import RibGeneratorEngine
from ui.batch_mode import BatchRunner

runner = BatchRunner()
runner.app.notebook.select(runner.app.tab_cam) # to ensure UI is built
params = runner.app.get_params()

engine = RibGeneratorEngine()
for i, y_local in enumerate(params['y_positions']):
    res = engine.generate_rib_at_y(params, y_local, i, params['rib_thick'], False, None)
    print(f"Rib {i}: res[14] len = {len(res[14])}")
