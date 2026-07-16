import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single
import unittest.mock as mock

root = tk.Tk()
app = RibGeneratorGUI_Single(root)

# We must bypass the dialog in load_tool_config or load_config.
# The user uses presets. Let's look at app.pm.
try:
    if hasattr(app, 'pm'):
        import json
        with open('preset/test.json', 'r') as f:
            data = json.load(f)
        app.pm.obj.data = data
        app.pm.obj._update_ui_from_data()
except Exception as e:
    print("Preset error:", e)
    
# Wait, just set the variables manually!
app.wing_span.set("200")
app.rib_interval.set("50")
app.export_te.set(True)

def mock_get_params():
    import json
    with open('preset/test.json', 'r') as f:
        data = json.load(f)
    data['y_positions'] = [0, 50, 100, 150, 200]
    data['export_te'] = True
    return data
    
app.get_params = mock_get_params

with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/test_single_out.glb'):
    with mock.patch('tkinter.messagebox.showerror', return_value=None):
        app.export_obj()

root.destroy()
