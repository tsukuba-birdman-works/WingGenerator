import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

frame = app.pm.obj.groups_frames['Cross Bracing']
for child in frame.winfo_children():
    if isinstance(child, tk.ttk.Label):
        print(child.cget('text'))
