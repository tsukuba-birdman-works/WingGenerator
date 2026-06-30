import sys
sys.path.append('.')
import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
try:
    vars_dict = app.get_all_vars()
    print("get_all_vars() succeeded!")
except AttributeError as e:
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)
