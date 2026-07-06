import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
print("Kerf Variable:", hasattr(app, 'foam_cut_kerf'))
if hasattr(app, 'foam_cut_kerf'):
    print("Value:", app.foam_cut_kerf.get())
    app.foam_cut_kerf.set("2.5")
    print("New Value:", app.foam_cut_kerf.get())
    print("Safe Float:", app.safe_float(app.foam_cut_kerf))
