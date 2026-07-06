import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from core.engine import RibGeneratorEngine

root = tk.Tk()
engine = RibGeneratorEngine()
app = RibGeneratorGUI_Batch(root)
# wait, RibGeneratorGUI_Batch initialization uses engine if passed?
# In main.py:
# from core.engine import RibGeneratorEngine
# engine = RibGeneratorEngine()
# tab1 = RibGeneratorGUI_Single(notebook, engine)
# wait, batch mode takes `engine` ?
