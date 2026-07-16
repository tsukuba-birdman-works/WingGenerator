import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single
from core.export_3d import Wing3DExporter

root = tk.Tk()
app = RibGeneratorGUI_Single(root)
root.update()

def load_mock(filepath):
    import json
    with open(filepath, 'r') as f:
        data = json.load(f)
    app.pm.obj.data = data
    app.pm.obj._update_ui_from_data()

app.pm.obj.load_preset = load_mock
app.pm.obj.load_preset('preset/test.json')
p = app.get_params()

print("y_positions length:", len(p['y_positions']))

import json
with open('preset/test.json', 'r') as f:
    d = json.load(f)
if 'te_start' in d:
    print("te_start:", d['te_start'])

root.destroy()
