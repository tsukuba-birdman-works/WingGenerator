import sys
import tkinter as tk
sys.path.append('.')
from ui.batch_mode import RibGeneratorGUI_Batch
root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
