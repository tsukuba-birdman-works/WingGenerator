import tkinter as tk
from ui.batch_mode import BatchModeApp
from core.engine import RibGeneratorEngine

root = tk.Tk()
engine = RibGeneratorEngine()
app = BatchModeApp(root, engine)

params = app._get_builder_params()
print("Jig params extracted:")
for k in ['jig_base_height', 'jig_base_thickness', 'jig_wall_thickness', 'jig_pillar_angle']:
    print(f"  {k}: {params.get(k, 'MISSING')}")
