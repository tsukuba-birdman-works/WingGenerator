import sys, json
sys.path.append('.')
from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
def load_mock(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    app.pm.obj.data = data
app.pm.obj.load_preset = load_mock
app.pm.obj.load_preset('preset/test.json')
app.update_ui_from_data()

p = app.get_params()
print(json.dumps(p, indent=2))
root.destroy()
