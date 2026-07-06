import tkinter as tk
from ui.batch_mode import BaseRibGeneratorGUI
root = tk.Tk()
app = BaseRibGeneratorGUI(root)
root.update()
print('UI loaded successfully')
root.destroy()
