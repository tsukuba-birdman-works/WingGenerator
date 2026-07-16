import tkinter as tk
from ui.batch_mode import BaseRibGeneratorGUI
import unittest.mock as mock

def run():
    root = tk.Tk()
    app = BaseRibGeneratorGUI(root)
    
    # Let's mock load_preset. Wait, where is load_preset?
    # In base_mode.py? Let's check.
    import json
    with open('preset/test.json', 'r') as f:
        data = json.load(f)
        
    try:
        app.pm.obj.data = data
        app.pm.obj._update_ui_from_data()
    except Exception as e:
        print("Failed to load preset UI:", e)
        # Just manually populate the dict?
        pass
        
    app.y_positions = [0, 50, 100]
    app.wing_span.set("100")
    app.rib_interval.set("50")
    
    with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/test_batch_ui_out.glb'):
        # Let's override _get_builder_params to inject the missing params
        orig_get = app._get_builder_params
        def my_get():
            p = orig_get()
            for k, v in data.items():
                if k not in p:
                    p[k] = v
            p['y_positions'] = [0, 50, 100]
            p['rib_thick'] = 2.0
            return p
        app._get_builder_params = my_get
        
        app.export_obj()
        print("Export finished!")

run()
