import json
import traceback
from core.export_3d import Wing3DExporter
from core.engine import RibGeneratorEngine

def test():
    with open('preset/test.json', 'r') as f:
        data = json.load(f)
    
    data['export_te'] = True
    
    # We need to run the full UI pipeline to populate the parameters properly
    import tkinter as tk
    from ui.batch_mode import BaseRibGeneratorGUI
    root = tk.Tk()
    app = BaseRibGeneratorGUI(root)
    
    # Simulate loading the preset
    try:
        # Batch mode UI has 'pm' which is a PresetManager?
        # Let's just use the engine directly if possible.
        pass
    except Exception as e:
        print("UI init error:", e)
        
    root.destroy()

test()
