import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
app.conn1_y.set('200.0')
app.conn1_type.set('Y-Shape')

params = app._get_builder_params()
print("Connectors parameter:", params.get('connectors'))
