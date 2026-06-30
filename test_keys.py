import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
try:
    params = app._get_builder_params()
    print("Params retrieved successfully without KeyError.")
except Exception as e:
    print("Error:", repr(e))
    import traceback
    traceback.print_exc()
