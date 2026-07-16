import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import unittest.mock as mock

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

# Mock filedialog to return preset/test.json
with mock.patch('tkinter.filedialog.askopenfilename', return_value='preset/test.json'):
    with mock.patch('tkinter.messagebox.showinfo'):
        app.load_config()

root.update()

# Mock ALL messageboxes and save path for export
with mock.patch('tkinter.filedialog.asksaveasfilename', return_value='scratch/batch_test_out.glb'):
    with mock.patch('tkinter.messagebox.showinfo') as si:
        with mock.patch('tkinter.messagebox.showwarning') as sw:
            with mock.patch('tkinter.messagebox.showerror') as se:
                app.export_obj()
                print("ShowInfo calls:", si.call_args_list)
                print("ShowWarning calls:", sw.call_args_list)
                print("ShowError calls:", se.call_args_list)

root.destroy()
