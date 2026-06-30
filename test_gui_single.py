import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single

root = tk.Tk()
app = RibGeneratorGUI_Single(root)
root.update_idletasks()
print("Single GUI built successfully without errors.")
