import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
try:
    print("Testing Single Mode...")
    gui_single = RibGeneratorGUI_Single(root)
    print("Single mode GUI initialized.")
    p1 = gui_single._get_params()
    print("Single mode params:", p1)
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("\nTesting Batch Mode...")
    gui_batch = RibGeneratorGUI_Batch(root)
    print("Batch mode GUI initialized.")
    p2 = gui_batch._get_builder_params()
    print("Batch mode params keys:", p2.keys())
    
    from core.engine import RibGeneratorEngine
    engine = RibGeneratorEngine()
    engine.generate_rib_at_y(p2, 0.0)
except Exception as e:
    import traceback
    traceback.print_exc()
