import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single

root = tk.Tk()
app = RibGeneratorGUI_Single(root)
root.update()

import unittest.mock as mock
with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/test_out.glb'):
    app.export_obj()

root.destroy()
