import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
root.update_idletasks()
print("GUI built successfully without errors.")
