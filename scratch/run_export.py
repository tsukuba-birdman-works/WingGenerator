import tkinter as tk
from ui.batch_mode import BaseRibGeneratorGUI
from core.preset_manager import PresetManager

root = tk.Tk()
app = BaseRibGeneratorGUI(root)
root.update()

# Load preset
app.pm.load_preset('preset/test.json')
root.update()

# Run export
params = app._get_builder_params()
print("Params extracted. y_positions length:", len(params.get('y_positions', [])))

from core.export_3d import Wing3DBuilder
from core.engine import RibGeneratorEngine
builder = Wing3DBuilder(RibGeneratorEngine(), params)
scene, xml = builder.build_geometry()
print("Exported meshes:", list(scene.keys()))

root.destroy()
