import tkinter as tk
from ui.batch_mode import BaseRibGeneratorGUI
from core.export_3d import Wing3DBuilder

root = tk.Tk()
app = BaseRibGeneratorGUI(root)
app.load_preset('preset/test.json')
root.update()

import unittest.mock as mock
with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/test_batch_out.glb'):
    app.export_3d()

root.destroy()
