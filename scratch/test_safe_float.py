import tkinter as tk
from ui.base_mode import BaseRibGeneratorGUI
root = tk.Tk()
app = BaseRibGeneratorGUI(root)
print(app.safe_float(tk.StringVar(value="13.4")))
