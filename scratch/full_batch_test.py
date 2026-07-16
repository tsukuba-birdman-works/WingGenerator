import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import unittest.mock as mock

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

# Load preset
app.pm.load_preset('preset/test.json')
root.update()

# Mock filedialog.asksaveasfilename
with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/batch_test_out.glb'):
    with mock.patch('tkinter.messagebox.showinfo'):
        app.export_obj()

root.destroy()
